"""
@file      response_generator.py
@author    Ryan Sargent(rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Provides a format_response function to generate API response data, as well
as templated static methods for standard API responses.
"""

from flask import jsonify, make_response, request
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response

from string_utils import sentence_case
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response


DEFAULT_MESSAGES = {
    "200": "Success",
    "201": "Successfully created new entry",
    "207": "Partial success",
    "400": "Invalid request",
    "401": "Unauthorized request",
    "403": "Insufficient permissions to perform this action",
    "404": "Could not find resource",
    "405": "Method not allowed",
    "409": "Entry already exists",
    "500": "Experienced an internal server error"
}


def format_response(code, status, message=None, body=None, headers={}):
    """
    Create and return a formatted flask.Response object
    """
    response_data = {}
    response_data["status"] = status

    if not message:
        message = DEFAULT_MESSAGES[str(code)]
    elif message.isupper():
        message = sentence_case(message)
    response_data["message"] = message

    if body:
        response_data["response"] = body

    response = make_response(jsonify(response_data), code)
    for key, val in headers.items():
        response.headers.add(key, val)

    return response


class APIResponses(object):

    @staticmethod
    def success(message=None, body=None):
        """
        Templeted method that returns a flask.Response object for successful requests.

        @param  request <obj>       flask.Request object
        @param  message <str>       Override for response.message
        @param  body <str>          Override for response.response (not included by default)

        @return flask.Response object
        """

        method = request.method
        message_overrides = {
            "POST": "Successfully created entry",
            "GET": "Successfully retrieved entry",
            "PUT": "Successfully updated entry",
            "PATCH": "Successfully updated entry",
            "DELETE": "Successfully deleted entry",
        }
        response_code = 201 if method == "POST" else 200

        if not message:
            message = message_overrides.get(method, f"HTTP method {method} not supported")

        return format_response(response_code, "Success", message, body)

    @staticmethod
    def failure(message=None, body=None):
        """
        Templeted method that returns a flask.Response object for failed requests.
        * Use `not_found` method for GET failures.

        @param  request <obj>       flask.Request object
        @param  message <str>       Override for response.message
        @param  body <str>          Override for response.response (not included by default)

        @return flask.Response object
        """

        method = request.method
        message_overrides = {
            "POST": "Unable to create entry",
            "PUT": "Unable to update entry",
            "DELETE": "Unable to delete entry",
        }

        if not message:
            message = message_overrides.get(method, f"HTTP method {method} not supported")

        return format_response(500, "Failure", message, body)

    @staticmethod
    def internal_error(message=None):
        """
        Templated method that returns a flask.Response object
        if the service encounters an error.
        """
        return format_response(500, "Failure", message)

    @staticmethod
    def not_found(message=None):
        """
        Templated method that returns a flask.Response object
        if the requested resource could not be found.
        """
        return format_response(404, "Failure", message)

    @staticmethod
    def bad_request(message=None, body=None):
        """
        Templated method that returns a flask.Response object
        for an invalid request.
        """
        return format_response(400, "Failure", message, body)

    @staticmethod
    def unauthorized(message=None):
        """
        Templated method that returns a flask.Response object
        for an unauthorized request.
        """
        return format_response(401, "Failure", message)

    @staticmethod
    def forbidden(message=None):
        """
        Templated method that returns a flask.Response object
        for a request to perform an action for which the user
        has not been granted permission.
        """
        return format_response(403, "Failure", message)

    @staticmethod
    def not_allowed(message=None, allowed_methods=None):
        """
        Templated method that returns a flask.Response object
        for a request which is not supported by the target resource.
        """
        headers = {
            'Allow': ", ".join(method.upper() for method in allowed_methods)
        }
        return format_response(405, "Failure", message, headers=headers)

    @staticmethod
    def conflict(message=None):
        """
        Templated method that returns a flask.Response object
        for a request which conflicts server-side. Typically used
        when a duplicate object already exists.
        """
        return format_response(409, "Failure", message)

    @staticmethod
    def multi_status(message=None):
        """
        Templated method that returns a flask.Response object
        for a request with both success and failure components
        which may leave the server in a "dirty" state.
        Do not use if state is not changed or was reverted.

        Ex: Suppose creating a key store requires multiple steps
                1. create a key group
                2. create a key template in the group
                3. link the template to the group's KRA
                4. update object permissions
            If step 3 fails and the key group can't be deleted,
            retrying the request would fail from the name conflict.
            Use this to indicate the request was a partial success.
        """
        return format_response(207, "Incomplete", message)

    @staticmethod
    def return_file(filename, file_data, mimetype):
        """
        Templated method that returns a werkzeug.wrappers.Response object
        for returning files.

        @param filename: name of the file to be returned
        @param file_data: data to be contained in the file to be returned
        @param mimetype: valid HTTP mimetype of the file to be returned
        """
        headers = Headers()
        headers.add('Content-Type', mimetype)
        headers.add('Content-Disposition', 'attachment', filename=filename)

        response = Response(file_data, 200, headers=headers, mimetype=mimetype)

        return response

    # Only used in UserGroups.delete
    # TODO: Remove when implementing Roles & Identities
    @staticmethod
    def missing_argument(argument=None):
        """
        Templated method that returns a flask.Response object
        for a request that did not supply a required argument.
        """
        return format_response(400, "Failure", f'Missing argument: {argument}')

    # Deprecated methods. For all "success" and "failure" methods, use the two methods above.
    # TODO: Replace all uses in views and remove these methods.
    @staticmethod
    def get_success(message=None, body=None):
        """
        Templated method that returns a flask.Response object
        for a successful GET request.
        """
        return format_response(200, "Success", message, body)

    @staticmethod
    def delete_failure(message=None):
        """
        Templated method that returns a flask.Response object
        for an unsuccessful DELETE request.
        """
        default_override = "Unable to delete specified entry"
        response_mssg = message or default_override

        return format_response(200, "Failure", response_mssg)

    @staticmethod
    def delete_success(message=None):
        """
        Templated method that returns a flask.Response object
        for a successful DELETE request.
        """
        default_override = "Resource successfully deleted"
        response_mssg = message or default_override

        return format_response(200, "Success", response_mssg)

    @staticmethod
    def post_failure(message=None):
        """
        Templated method that returns a flask.Response object
        for an unsuccessful POST request.
        """
        default_override = "Unable to create entry."
        response_mssg = message or default_override

        return format_response(200, "Failure", response_mssg)

    @staticmethod
    def post_success(message=None, body=None):
        """
        Templated method that returns a flask.Response object
        for a successful POST request.
        """
        return format_response(201, "Success", message, body)

    @staticmethod
    def put_failure(message=None):
        """
        Templated method that retruns a flask.Response object
        for an unsuccessful PUT request.
        """
        default_override = "Unable to update entry"
        response_mssg = message or default_override

        return format_response(200, "Failure", response_mssg)

    @staticmethod
    def put_success(message=None, body=None):
        """
        Templated method that returns a flask.Response object
        for a successful PUT request.
        """
        default_override = "Successfully updated entry"
        response_mssg = message or default_override

        return format_response(200, "Success", response_mssg, body)
