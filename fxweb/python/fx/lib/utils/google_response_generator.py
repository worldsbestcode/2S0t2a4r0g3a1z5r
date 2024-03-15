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
as templated static methods for google API responses.
"""

from flask import jsonify, make_response

from lib.utils.string_utils import sentence_case
from enum import Enum

GCODE_TO_INT = {
        'OK': 0,
        'CANCELLED': 1,
        'UNKNOWN': 2,
        'INVALID_ARGUMENT': 3,
        'DEADLINE_EXCEEDED': 4,
        'NOT_FOUND': 5,
        'ALREADY_EXISTS': 6,
        'PERMISSION_DENIED': 7,
        'UNAUTHENTICATED': 16,
        'RESOURCE_EXHAUSTED': 8,
        'FAILED_PRECONDITION': 9,
        'ABORTED': 10,
        'OUT_OF_RANGE': 11,
        'UNIMPLEMENTED': 12,
        'INTERNAL': 13,
        'UNAVAILABLE': 14,
        'DATA_LOSS': 15,
}

GCODE_TO_HTTP = {
    'OK':                   200,
    'CANCELLED':            499,
    'UNKNOWN':              500,
    'INVALID_ARGUMENT':     400,
    'DEADLINE_EXCEEDED':    504,
    'NOT_FOUND':            404,
    'ALREADY_EXISTS':       409,
    'PERMISSION_DENIED':    403,
    'UNAUTHENTICATED':      401,
    'RESOURCE_EXHAUSTED':   429,
    'FAILED_PRECONDITION':  400,
    'ABORTED':              409,
    'OUT_OF_RANGE':         400,
    'UNIMPLEMENTED':        501,
    'INTERNAL':             500,
    'UNAVAILABLE':          503,
    'DATA_LOSS':            500,
}

STR_TO_GCODE = {
    "Invalid argument":     'INVALID_ARGUMENT',
    "Not found":            'NOT_FOUND',
    "Permission denied":    'PERMISSION_DENIED',
    "Unauthenticated":      'UNAUTHENTICATED',
    "Unimplemented":        'UNIMPLEMENTED',
    "Internal":             'INTERNAL',
    "Unavailable":          'UNAVAILABLE',
    # RK Errors
    "NO PERMISSION":        'PERMISSION_DENIED',
    "INVALID USER":         'PERMISSION_DENIED',
    "AUTH ERROR":           'UNAUTHENTICATED',
}


def format_response_error(msg_type, g_code, message=None, body=None):
    """
    Create and return a formatted flask.Response object
    """
    response_data = {}
    if msg_type == GAPIType.Ekms:
        response_data['code'] = GCODE_TO_INT.get(g_code, 5)
    response_data['message'] = message

    if body:
        response_data['details'] = body

    resp_code = GCODE_TO_HTTP.get(g_code, 500)
    return make_response(jsonify(response_data), resp_code)


def format_response(code, body=None, headers=None):
    """
    Create and return a formatted flask.Response object with custom body
    """
    return make_response(jsonify(body), code, headers)


def bad_ekms_request(body=None):
    """
    Creates ekms bad request message body
    """
    bad_req = {}
    bad_req['@type'] = 'type.googleapis.com/google.rpc.BadRequest'
    fields_val_list = []
    for value in body:
        field_val = {'field': value}
        fields_val_list.append(field_val)

    bad_req['fieldViolations'] = fields_val_list

    return [bad_req]


def bad_cse_request(body=None):
    """
    Creates gcse bad request message body
    """
    return ','.join(body) if body else ''


class GAPIType(Enum):
    Invalid = 0
    Ekms = 1
    Cse = 2


class GAPIResponses(object):

    @staticmethod
    def get_path_type(path):
        """
        return true if path is ekms request
        """
        gapiType = GAPIType.Invalid
        if path:
            msg_index = path.find('/key-encrypt')
            if msg_index != -1:
                if path.find('/external', msg_index) != -1:
                    gapiType = GAPIType.Ekms
                elif path.find('/client', msg_index) != -1:
                    gapiType = GAPIType.Cse

        return gapiType

    @staticmethod
    def get_error(message=None):
        """
        get error code from message
        """
        str_error = message.split(":", 1)[0]
        return STR_TO_GCODE.get(str_error, 'NOT_FOUND')

    @staticmethod
    def success(body=None):
        """
        Templated method that returns a flask.Response object
        for a successful request.
        """
        return format_response(200, body)

    @staticmethod
    def error(msg_type, error, message=None, body=None):
        """
        Templated method that returns a flask.Response object
        for a request that gave an error.
        """
        return format_response_error(msg_type, error, message, body)

    @staticmethod
    def unauthorized(msg_type=None, message=None):
        """
        Templated method that returns a flask.Response object
        for a request that was unauthorized.
        """
        return format_response_error(msg_type, 'UNAUTHENTICATED', 'Unauthenticated: ' + message)

    @staticmethod
    def invalid_argument(msg_type=None, message=None):
        """
        Templated method that returns a flask.Response object
        for a request that supplied a invalid argument.
        """
        return format_response_error(msg_type, 'INVALID_ARGUMENT', 'Invalid Argument: ' + message)

    @staticmethod
    def internal_error(msg_type=None):
        """
        Templated method that returns a flask.Response object
        for a request that supplied a internal error.
        """
        return format_response_error(msg_type, 'INTERNAL', 'Internal error')

    @staticmethod
    def forbidden(msg_type=None, message=None):
        """
        Templated method that returns a flask.Response object
        for a request that supplied a permission denied.
        """
        return format_response_error(msg_type, 'PERMISSION_DENIED', 'Permission denied:' + message)

    @staticmethod
    def not_found(msg_type=None, message=None):
        """
        Templated method that returns a flask.Response object
        for a request that was not found
        """
        if not message:
            message = "Could not find resource"
        return format_response_error(msg_type, 'NOT_FOUND', 'Not Found: ' + message)

    @staticmethod
    def bad_request(msg_type=None, message=None, body=None):
        """
        Templated method that returns a flask.Response object
        for a request that supplied a invalid argument.
        """

        format_body = None
        if (msg_type == GAPIType.Ekms):
            format_body = bad_ekms_request(body)
        else:
            format_body = bad_cse_request(body)

        return format_response_error(msg_type, 'INVALID_ARGUMENT', message, format_body)
