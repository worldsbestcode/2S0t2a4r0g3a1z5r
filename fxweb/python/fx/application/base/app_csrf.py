"""
@file      app_csrf.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Checks that the CSRF token is valid
"""
import typing
from functools import wraps
from flask import request
from flask_login import current_user
from auth import login_required
from base_exceptions import UserNotAuthenticated
from urllib.parse import urlparse
from rkweb.config import WebConfig
from rkweb.session import AuthSession

if typing.TYPE_CHECKING:
    from lib.auth.user import User
    current_user: User

def csrf_required(func):
    '''
    Ensures that the CSRF token is valid before calling
    the actual view that this decorates
    '''
    @login_required
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # We won't find a token so exit early
        if current_user.context is None:
            raise UserNotAuthenticated('Invalid user session.')

        # Get valid origins from rkweb code
        RkWebConfigInit.init()
        list_origins = WebConfig.cached_origins()

        # headers the browser sent in the request
        headers = request.headers
        request_token = headers.get('X-Fxsrf-Token')
        request_referer = headers.get('Referer')
        request_origin = headers.get('Origin')

        # Local cardbrowser dashboard allow localhost origin
        if request.environ['SERVER_PORT'] == '9876':
            list_origins = set(list_origins)
            list_origins.add('https://127.0.0.1:9876')
            list_origins.add('https://localhost:9876')

        # Configuration not ready
        if len(list_origins) == 0:
            print("No valid origins configured.")
            pass

        # check if user agent is vulnerable
        elif not current_user.requires_csrf:
            pass

        # check if the CSRF token is missing or incorrect
        elif not check_token(request_token):
            raise UserNotAuthenticated('Invalid CSRF token.')

        # check if a valid CSRF token is all we need
        elif not current_user.csrf_check_origin:
            pass

        # check if the origin header is missing or incorrect
        elif request_origin in list_origins or '*' in list_origins:
            pass

        # check if the referer header is missing or incorrect
        elif check_referer(request_referer, list_origins):
            pass

        # reject requests with a bad origin and referer
        else:
            raise UserNotAuthenticated('Invalid origin or referer.')

        # safe to continue
        return func(*args, **kwargs)

    return decorated_view

def check_referer(referer, origins):
    '''Check if any of the referers listed match
    Arguments:
        referer: The HTTP header received
        origins: The list of acceptable uris
    Returns:
        True if one of the URIs matches else false
    '''
    if referer is None:
        return False
    referer_netloc = urlparse(referer).netloc
    acceptable_netlocs = set()
    for uri in origins:
        acceptable_netlocs.add(urlparse(uri).netloc)
    return referer_netloc in acceptable_netlocs

def check_token(request_token):
    '''
    Compare the token from the request to the assigned CSRF token
    '''
    if request_token is not None:
        # Matches fxweb CSRF token
        if request_token == current_user.context.csrf_token:
            return True
        # Try to get updated rkweb CSRF token
        rkweb_auth = AuthSession.get()
        if rkweb_auth.csrf_token and rkweb_auth.csrf_token != current_user.context.csrf_token:
            current_user.context.csrf_token = rkweb_auth.csrf_token
        # Does it match now?
        return request_token == current_user.context.csrf_token
    else:
        return False

# Bridge async rkweb with sync fxweb
import asyncio
import datetime
import threading
class RkWebConfigInit:
    last_update = None
    lock = threading.Lock()
    def init() -> None:
        try:
            RkWebConfigInit.lock.acquire()
            # Only refresh once every 5 minutes
            if RkWebConfigInit.last_update and (RkWebConfigInit.last_update + datetime.timedelta(minutes=5)) > datetime.datetime.utcnow():
                return None
            try:
                loop = asyncio.get_event_loop()
            except:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            coro = WebConfig.get_origins()
            loop.run_until_complete(coro)
        finally:
            RkWebConfigInit.lock.release()
