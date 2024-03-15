"""
@file      token_authentication.py
@author    David Neathery (dneathery@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Handles token authentication
"""

import functools
import re
import time

from flask import request, g
from auth import login_required
from flask_login import current_user
from gevent.lock import RLock

from app_csrf import csrf_required
from application_log import ApplicationLogger
from conn_exceptions import CannotConnectException
from lib.utils.google_response_generator import GAPIResponses
from lib.utils.google_response_generator import GAPIType
from lib.utils.response_generator import APIResponses
from string_utils import string_is_jwt, string_is_api_key
from token_context import TokenContext


def get_allowed_jwt_headers():
    """Get the allowed jwt headers
    Returns: headers  Containing the headers checked for JWT
    """
    try:
        from app_config import AppConfig
    except ImportError:
        return ['Authorization']

    config = AppConfig.get_config()
    return config.jwt_headers


def get_allowed_api_key_headers():
    """Get the allowed api key headers
    Returns: headers  Containing the headers checked for API Keys
    """
    try:
        from app_config import AppConfig
    except ImportError:
        return ['X-API-Key']

    config = AppConfig.get_config()
    return config.api_key_headers


def jwt_required(view):
    """
    Decorate a view to require that JSON Web Tokens are supplied in request
    """
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        for header in get_allowed_jwt_headers():
            header_auth = request.headers.get(header, '')

            # Break at the first valid header custom headers are checked first
            if header_auth:
                break

        pattern = r'^Bearer (?P<token>.*)$'
        match = re.match(pattern, header_auth)
        if not match:
            return APIResponses.unauthorized('Resource requires Bearer token')
        token = match.group('token')
        if not string_is_jwt(token):
            return APIResponses.bad_request('Malformed JWT: ' + token)
        else:
            g.jwt = token
            return view(*args, **kwargs)
    return wrapper


def jwt_optional(view):
    """
    Decorate a view to determine if JSON Web Tokens are supplied in request
    """
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        for header in get_allowed_jwt_headers():
            header_auth = request.headers.get(header, '')

            # Break at the first valid header custom headers are checked first
            if header_auth:
                break

        pattern = r'^Bearer (?P<token>.*)$'
        match = re.match(pattern, header_auth)
        token = ''
        if match:
            token = match.group('token')
            if string_is_jwt(token):
                g.jwt = token
                return view(*args, **kwargs)

        # Also check for API Keys
        for header in get_allowed_api_key_headers():
            header_auth = request.headers.get(header, '')

            # Break at the first valid header custom headers are checked first
            if header_auth:
                break

        key = ''
        if header_auth:
            # Strip leading 'Bearer ' or 'API:'
            key = header_auth
            if key.startswith('Bearer '):
                key = key[7:]
            if key.startswith('API:'):
                key = key[4:]

            if string_is_api_key(key):
                g.jwt = "API:" + key
                return view(*args, **kwargs)

        # Check for badly formatted token / key
        if token:
            return APIResponses.bad_request('Malformed JWT: ' + token)
        elif key:
            return APIResponses.bad_request('Malformed API Key: ' + key)

        # Check login required
        if current_user is None or current_user.requires_csrf:
            return csrf_required(view)(*args, **kwargs)

        return login_required(view)(*args, **kwargs)

    return wrapper


def google_jwt_required(view):
    """
    Decorate a view to require that JSON Web Tokens are supplied in request with google error response
    """
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        for header in get_allowed_jwt_headers():
            header_auth = request.headers.get(header, '')

            # Break at the first valid header custom headers are checked first
            if header_auth:
                break

        pattern = r'^Bearer (?P<token>.*)$'
        match = re.match(pattern, header_auth)
        if not match:
            return GAPIResponses.unauthorized(GAPIType.Ekms, 'Resource requires Bearer token')
        token = match.group('token')
        if not string_is_jwt(token):
            return GAPIResponses.unauthorized(GAPIType.Ekms, 'Malformed JWT: ' + token)
        else:
            g.jwt = token
            return view(*args, **kwargs)
    return wrapper


class JWTContextPool(object):
    """
    Maintains a map of open connection contexts for tokens
    """
    def __init__(self, server_interface):
        self.interface = server_interface
        self.config = server_interface.program.config
        self.items = {}  # holds the active contexts
        self.lock = RLock()  # locks both items and expired_items
        self.inactive_time = 30  # seconds before an inactive context is considered "expired"
        self.expired_items = []  # holds cache of invalidated contexts for open connections
        self.max_expired_size = 10  # max size of expired_items
        self.last_reclamation = time.time()  # timestamp of last time _reclaim completed

    def acquire(self, token):
        """
        Get a context manager that will yield a context for token
        """
        return JWTContextManager(pool=self, token=token)

    def _fetch(self, token):
        """
        Get a context for this token, prefer one that already exists
        """
        with self.lock:
            context = self.items.get(token)
            if context is None:
                context = self._get_a_context()
                self.items[token] = context
        return context

    def _create_new_context(self):
        """
        Create a new context but don't open a connection with it
        """
        new_context = TokenContext(
            to_address=self.config.host_address,
            synch_req_tag=self.config.send_tag,
            synch_resp_tag=self.config.receive_tag,
        )
        return new_context

    def connect_context(self, context):
        """
        Opens a connection if not already connected, otherwise it will be closed

        Must be locked by the caller
        """
        try:
            context.connected = self.interface.connect(context)
        except CannotConnectException:
            ApplicationLogger.error('Failed to connect to server')
            raise

    def _get_a_context(self):
        """
        Try to repurpose an old connection, otherwise create a new one
        """
        self._reclaim()
        context = None
        with self.lock:
            if self.expired_items:
                context = self.expired_items.pop()
                context.token = None
        if context is None:
            context = self._create_new_context()
        return context

    def remove_context(self, context):
        """
        Remove a context from the pool
        """
        with self.lock:
            try:
                self.expired_items.remove(context)
            except ValueError:
                pass
            for token in list(self.items.keys()):
                if self.items[token] is context:
                    del self.items[token]
        try:
            self.interface.conn_handler.remove(context)
        except OSError:
            pass  # if the connection was already closed unexpectedly, nothing to do

    def _reclaim(self):
        """
        Invalidate old contexts to be reused or destroyed
        """
        # only run occasionally:
        now = time.time()
        if now < self.last_reclamation + self.inactive_time:
            return False

        victims = []
        victims_to_close = []
        cutoff_time = now - self.inactive_time
        with self.lock:
            # identify any contexts which are expired:
            for token, context in self.items.items():
                if context.access_time < cutoff_time and context.in_use == 0:
                    context.token = None
                    victims.append(token)
            # move them to the cache or close them:
            for token in victims:
                context = self.items.pop(token)
                if len(self.expired_items) < self.max_expired_size:
                    self.expired_items.append(context)
                else:
                    victims_to_close.append(context)
            self.last_reclamation = now

        # close extra connections if we're already at max:
        for context in victims_to_close:
            try:
                self.interface.conn_handler.remove(context)
            except OSError:
                pass  # if the connection was already closed unexpectedly, nothing to do
        return True


class JWTContextManager(object):
    """
    Implements the context manager protocol for a JWTContextPool
    """
    def __init__(self, pool, token):
        self.pool = pool
        self.token = token
        self.hold_lock = False  # stall subsequent requests if not yet connected

    def __enter__(self):
        context = self.pool._fetch(self.token)

        context.lock.acquire()
        try:
            if not context.connected:
                self.hold_lock = True
                self.pool.connect_context(context)
            elif context.token != self.token:
                # connection was recycled; hold lock for re-authentication
                self.hold_lock = True
            context.access_time = time.time()
            context.in_use += 1
        finally:
            if not self.hold_lock:
                context.lock.release()

        self.context = context
        return context

    def __exit__(self, cls, e, traceback):
        if e is not None:
            # connection may have closed, so try not to keep it around:
            self.pool.remove_context(self.context)

        if not self.hold_lock:
            self.context.lock.acquire()
        try:
            self.context.in_use -= 1
        finally:
            self.context.lock.release()

        return None  # do not capture the exceptions
