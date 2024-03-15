"""
@file      rk_host_application/rk_host_exceptions.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Exceptions for Host API middleware applications
"""

class HAPIError(Exception):
    """
    Base class for Host API exceptions.
    """


class FunctionNotSupportedError(HAPIError):
    """
    The request failed because the command is disabled or does not exist.
    """


class UserNotLoggedInError(HAPIError):
    """
    The request failed because the user is not logged in.
    """


class FailedRAVD(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message


class DisallowedCharacters(Exception):
    pass
