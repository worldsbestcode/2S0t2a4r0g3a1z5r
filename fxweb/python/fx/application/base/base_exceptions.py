"""
@file      base_exceptions.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Adds exceptions for web application
"""

from flask import jsonify, request

from collections import namedtuple
from static_content_view import create_static_response
from response_generator import APIResponses
from app_config import AppConfig

# What type of request created the exception
RequestState = namedtuple('RequestState', ['in_request', 'in_api_request'])


def get_request_state() -> RequestState:
    """Allow exceptions to decide how to handle themselves
    Returns: A request state tuple
        in_request: True if the we are in a request right now
        in_api_request:  True if the request begins with the api prefix
    """
    try:
        path = request.path
    except RuntimeError:
        # No request object exists
        return RequestState(False, False)
    else:
        # The JSON API Always returns JSON errors
        in_api = False
        for elem in path.split('/'):
            if elem[0:1] == 'v':
                try:
                    vers = int(elem[1:])
                    in_api = True
                except:
                    pass
        return RequestState(True, in_api)


class MiddlewareException(Exception):
    """
    Base middleware exception class.
    This class forces subclasses to implement registry functions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.unhandled_args = kwargs
        self.request_state = get_request_state()

    @property
    def page(self):
        """
        Page to display used in the default exception handler
        Our nginx config redirects to 40x.html when an error code is thrown
        so this is never received by the user
        """
        return 'unauthorized.html'

    @property
    def code(self):
        """
        Code to send during exception
        """
        return 401

    def _handle_exception(self, app=None):
        """Error handling is context sensitive"""
        if self.request_state.in_api_request:
            return self.api_response(app)
        if self.request_state.in_request:
            return self.redirect_response(app)

        # The exception happened outside of a request. Re-raise ourselves.
        # This will dump a stack trace in the uwsgi logs
        raise self

    def api_response(self, app=None):
        """Handle api responses 401 is the default"""
        return APIResponses.unauthorized(str(self))

    def redirect_response(self, app=None):
        """Handle redirect responses"""
        return create_static_response('/', self.page, code=self.code)

    def log_exception(self, logger):
        """
        Any exception logging that may need to take place
        :param logger the program logging function
        """
        logger.error(str(self))
        if self.unhandled_args:
            logger.debug(f'Unhandled exception key-word arguments {self.unhandled_args.keys()}')

    @staticmethod
    def _error_string(err_msg='', **kwargs):
        """
        Use the err_msg as a template returning none if a key error occurs
        this doesn't check for unneeded arguments
        :param err_msg the message template
        :param kwargs the key, value arg list
        """
        for key, value in list(kwargs.items()):
            # To avoid None substitution
            if value is None:
                kwargs[key] = 'unknown {}'.format(key)

        result = err_msg.format(**kwargs)
        return result


class UserNotAuthenticated(MiddlewareException):
    """
    A class for session authentication errors
    """
    def _handle_exception(self, app=None):
        """Error handling is context sensitive"""
        if self.request_state.in_api_request:
            return self.api_response(app)
        else:
            return self.redirect_response(app)


class UserNotLoggedIn(MiddlewareException):
    """
    A class for user login errors.
    """
    def __init__(self, user, is_group, object_id):

        self.user = user
        self.is_group = is_group
        self.object_id = object_id

        MiddlewareException.__init__(self)

    def _handle_exception(self, app=None):
        """Error handling is context sensitive"""
        if self.request_state.in_api_request:
            return self.api_response(app)
        else:
            return self.redirect_response(app)


class UnroutableRequest(MiddlewareException):
    """
    A class for errors in routing a request
    """
    def _handle_exception(self, app=None):
        return jsonify({'status': 'Failure', 'message': str(self)}), 400


class SerializationError(Exception):
    """
    Message serialization failed
    """
    def __init__(self, message=None, field_name=None):
        self.message = message
        self.field_name = field_name


BASE_EXCEPTIONS = [
    UserNotAuthenticated,
    UserNotLoggedIn,
    UnroutableRequest,
]
