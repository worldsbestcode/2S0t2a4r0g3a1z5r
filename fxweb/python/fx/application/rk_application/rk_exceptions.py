"""
@file      rk_exceptions.py
@author    Matthew Seaworth(mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Exceptions for remotekey products
"""
import fx
from flask import jsonify
from base_exceptions import MiddlewareException


class CacheUpdateException(MiddlewareException):
    """
    An exception for cache errors that occur in server code
    """
    err_msg = 'Cache caught exception {exception}'

    def __init__(self, exception=None, *args, **kwargs):
        """
        :param exception The rk exception thrown
        :param args The tuple args passed to parent
        :param kwargs The dict args passed to parent
        """
        if exception is not None:
            msg = self._error_string(self.err_msg, exception=exception)
        elif len(args) == 0 and len(kwargs) == 0:
            msg = 'Cache caught exception'

        if msg:
            MiddlewareException.__init__(self, msg, *args, **kwargs)
        else:
            MiddlewareException.__init__(self, *args, **kwargs)


class PermissionsException(MiddlewareException):
    """
    This exception is for when a user is not allowed to perform the
    attempted action
    """


class ObjectActionException(MiddlewareException):
    """
    Template for object action exceptions
    """
    err_msg = 'Could not {action} object with manager {manager} and ID {oid}{reason}'
    action = None  # The action being performed overwritten in subclasses

    def __init__(self, manager=None, oid=None, reason=None, *args, **kwargs):
        """
        :param manager The manager the object belongs to
        :param oid The id of the object
        """
        if oid is None:
            oid = 'unknown id'

        if reason is not None:
            reason = ", because " + reason
        else:
            reason = ""

        msg = None
        if manager is not None:
            error_args = {
                'action': self.action,
                'manager': manager,
                'oid': oid,
                'reason': reason
            }

            msg = self._error_string(self.err_msg, **error_args)
        elif len(args) == 0 and len(kwargs) == 0:
            msg = 'Could not {} object'.format(self.action)

        if msg:
            MiddlewareException.__init__(self, msg, *args, **kwargs)
        else:
            MiddlewareException.__init__(self, *args, **kwargs)

    def _handle_exception(self, app=None):
        """Return the object exception"""
        return jsonify(status='Failure', message=str(self))


class ObjectNotAddedException(ObjectActionException):
    """
    If an object add fails
    """
    action = 'add'


class ObjectNotDeletedException(ObjectActionException):
    """
    If an object delete fails
    """
    action = 'delete'


class ObjectNotFoundException(ObjectActionException):
    """
    This exception gets thrown when the server server cant find an object
    """
    action = 'find'


class ObjectNotModifiedException(ObjectActionException):
    """
    If one of the create/delete operations fails
    during update
    """
    action = 'modify'


class ObjectNotValidatedException(ObjectActionException):
    """
    If one of the create/delete operations fails
    during update
    """
    action = 'validate'


class ObjectNotFilteredException(ObjectActionException):
    """
    If one of the create/delete operations fails
    during update
    """
    action = 'filter'


REMOTEKEY_EXCEPTIONS = [
    CacheUpdateException,
    ObjectNotAddedException,
    ObjectNotDeletedException,
    ObjectNotFoundException,
    ObjectNotModifiedException,
    ObjectNotValidatedException,
    PermissionsException,
    ObjectNotFilteredException
]
