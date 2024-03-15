"""
@file      conn_exceptions.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Adds connection based exceptions for web application
"""
from flask_login import current_user, logout_user
from auth import User

import fx
from base_exceptions import MiddlewareException


class ErrorOnReadException(MiddlewareException):
    """
    An error occurred during a read
    """


class ErrorOnWriteException(MiddlewareException):
    """
    An error occurred during a write
    """


class MissingConnectionException(MiddlewareException):
    """
    This exception gets thrown when the server
    disconnects from the middleware unexpectedly
    """
    def __init__(self, *args, **kwargs):
        """
        Remove the user object and session if this exception is thrown
        """
        MiddlewareException.__init__(self, *args, **kwargs)
        User.remove(current_user.get_id(), logout_user)


class CannotConnectException(MiddlewareException):
    """
    If a connection to the server fails
    """


class ServerConnectionTimeout(MiddlewareException):
    """
    The server didn't respond to a request
    """


class InvalidMessageException(MiddlewareException):
    """
    For when an invalid message is received
    """
    def __init__(self, callback=None, *args, **kwargs):
        """
        :param callback Function to handle extra server response
        """
        MiddlewareException.__init__(self, *args, **kwargs)
        self.callback = callback

    def _handle_exception(self, app=None):
        """
        Handle an invalid message
        """
        if self.callback is not None:
            return self.callback(self, app)

        return super(InvalidMessageException, self)._handle_exception(app)


class InvalidExcryptMessage(InvalidMessageException):
    """
    For when we get an invalid excrypt message
    """


class NoSuchExcryptCommand(InvalidMessageException):
    """
    For when an excrypt message command indicator is unknown
    """
    def __init__(self, cmd_name='(None)', *args, **kwargs):
        self.cmd_name = cmd_name
        InvalidMessageException.__init__(self)


CONNECTION_EXCEPTIONS = [
    ErrorOnReadException,
    ErrorOnWriteException,
    MissingConnectionException,
    ServerConnectionTimeout,
    InvalidMessageException,
    InvalidExcryptMessage,
    ServerConnectionTimeout,
    NoSuchExcryptCommand,
]
