"""
@file      rk_host_flask_handlers.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Register Host API exception handlers with Flask application
"""
import binascii
import traceback
from json.decoder import JSONDecodeError

from flask import Flask, Request, request
from flask_login import current_user, logout_user
from marshmallow.exceptions import ValidationError

from application_log import ApplicationLogger as Logger
from auth import User
from base.base_exceptions import SerializationError
from base import base_exceptions
from lib.utils import hapi_parsers as parsers
from lib.utils.response_generator import APIResponses, format_response
from rk_host_application import rk_host_exceptions
from lib.utils.general_response_generator import GeneralResponses


def set_error_handlers(app: Flask, config):

    @app.errorhandler(405)
    def handle_405(exception):
        """
        Handles method not allowed error
        """
        return APIResponses.not_allowed(allowed_methods=exception.valid_methods)

    @app.errorhandler(404)
    def handle_404(exception):
        return GeneralResponses.not_found(request.path)

    @app.errorhandler(401)
    def handle_401(exception):
        return GeneralResponses.unauthorized(request.path, exception.description)

    @app.errorhandler(ValidationError)
    def handle_validation_error(exception):
        """
        Handle Marshmallow ValidationError exception
        """
        error_dict = parsers.flatten_dict(exception.normalized_messages())
        error_message = 'Validation error'
        error_list = []

        for field, errors in error_dict.items():
            for error in errors:
                error_list.append('{}: {}'.format(error.rstrip('.!?'), field))

        return GeneralResponses.bad_request(request.path, error_message, error_list)

    @app.errorhandler(Exception)
    def handle_internal_server_error(exception):
        """
        Catch-all handler for exceptions
        """
        view_name = 'unknown view'
        request_method = 'unknown'
        endpoint = request.url_rule and request.url_rule.endpoint
        method_function = endpoint and app.view_functions.get(endpoint, None)

        if method_function:
            view_name = method_function.view_class.__name__
            request_method = request.method

        log_message = 'Error handling {} {} method: {}'.format(view_name, request_method, exception)
        Logger.error(log_message)

        # DEBUG: Uncomment this to get back traces
        #raise exception

        if config.log_level == 'debug':
            traceback.print_exc()
            return APIResponses.get_success(log_message, traceback.format_exc().splitlines())

        return GeneralResponses.internal_error(request.path)

    if (config.server_type == 'byok'):
        @app.errorhandler(503)
        @app.errorhandler(500)
        @app.errorhandler(422)
        @app.errorhandler(409)
        @app.errorhandler(404)
        @app.errorhandler(403)
        @app.errorhandler(401)
        @app.errorhandler(400)
        def handle_error_codes(exception):
            try:
                code = exception.code
            except AttributeError:
                code = 500
            try:
                data = exception.data
            except AttributeError:
                data = {}
            return format_response(code=code, status='Failure', message=data.get('message'))

    def on_json_loading_failed(_, exception):
        """
        Called if request.get_json() fails to decode the message body.
        """
        if isinstance(exception, UnicodeDecodeError):
            # Workaround for flask.json.loads, tries to decode bytes as UTF-8 before json.loads
            new_exc = JSONDecodeError('', '', 0)
            new_exc.args = (str(exception),)
            raise new_exc

        raise  # reraise JSONDecodeError, a return would become the get_json() response

    Request.on_json_loading_failed = on_json_loading_failed

    @app.errorhandler(JSONDecodeError)
    def handle_json_decode_error(exception):
        """
        Handles errors from attempting to decode an invalid JSON document.
        """
        message = 'Unable to parse request body as JSON.'

        return GeneralResponses.bad_request(request.path, message, exception.args)

    @app.errorhandler(binascii.Error)
    def handle_binascii_error(exception):
        """
        Handles errors converting strings to/from base64, hex, etc.
        """
        return GeneralResponses.bad_request(request.path, None, str(exception))

    @app.errorhandler(rk_host_exceptions.UserNotLoggedInError)
    def handle_not_logged_in(exception):
        """
        Handles unexpected command response that the user is not logged
        """
        User.remove(current_user.get_id(), logout_user)  # TODO(@dneathery): Use ExceptionRegistry
        return GeneralResponses.unauthorized(request.path, 'User not logged in')

    @app.errorhandler(base_exceptions.UserNotAuthenticated)
    def handle_base_not_logged_in(exception):
        """
        Handles unexpected command response that the user is not logged
        """
        return GeneralResponses.unauthorized(request.path, 'User not logged in')

    @app.errorhandler(rk_host_exceptions.FunctionNotSupportedError)
    def handle_disabled_feature(exception):
        """
        Handles a FUNCTION NOT SUPPORTED response to a HAPI request
        """
        return GeneralResponses.forbidden(request.path, 'Requested operation not enabled on this device')

    @app.errorhandler(SerializationError)
    def handle_bad_input(exception: SerializationError):
        """
        Handle failed serialization due to bad input
        """
        message = exception.message or 'Invalid input'
        field = exception.field_name or ''
        # Do not reveal the names of "private" translator fields
        if field.startswith('_'):
            field = ''
        combined = '{}{}{}'.format(
            message.rstrip('.?!'),
            ': ' if field else '.',
            field,
        )
        return GeneralResponses.bad_request(request.path, None, combined)
