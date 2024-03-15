"""
@file      google_response_generator.py
@author    Stephen Jackson(sjackson@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Provides a format_response function to generate API response data, as well
as templated static methods for kmes and google API responses.
"""

from lib.utils.response_generator import APIResponses
from lib.utils.google_response_generator import GAPIResponses
from lib.utils.google_response_generator import GAPIType


class GeneralResponses(object):

    @staticmethod
    def unauthorized(path, message=None):
        """
        Templated method that returns a flask.Response object
        for a request that was unauthorized.
        """
        msg_type = GAPIResponses.get_path_type(path)
        if msg_type != GAPIType.Invalid:
            return GAPIResponses.unauthorized(msg_type, message)
        else:
            return APIResponses.unauthorized()

    @staticmethod
    def internal_error(path):
        """
        Templated method that returns a flask.Response object
        for a request that supplied a internal error.
        """
        msg_type = GAPIResponses.get_path_type(path)
        if msg_type != GAPIType.Invalid:
            return GAPIResponses.internal_error(msg_type)
        else:
            return APIResponses.internal_error()

    @staticmethod
    def forbidden(path, message=None):
        """
        Templated method that returns a flask.Response object
        for a request that supplied a permission denied.
        """
        msg_type = GAPIResponses.get_path_type(path)
        if msg_type != GAPIType.Invalid:
            return GAPIResponses.unauthorized(msg_type, message)
        else:
            return APIResponses.unauthorized(message)

    @staticmethod
    def not_found(path):
        """
        Templated method that returns a flask.Response object
        for a request that was not found
        """
        msg_type = GAPIResponses.get_path_type(path)
        if msg_type != GAPIType.Invalid:
            return GAPIResponses.not_found(msg_type)
        else:
            return APIResponses.not_found()

    @staticmethod
    def bad_request(path, message=None, error_list=None):
        """
        Templated method that returns a flask.Response object
        for a request that supplied a invalid argument.
        """
        msg_type = GAPIResponses.get_path_type(path)
        if msg_type != GAPIType.Invalid:
            return GAPIResponses.bad_request(msg_type, message if message else 'Invalid message', error_list)
        else:
            return APIResponses.bad_request(message, {'errors': error_list})
