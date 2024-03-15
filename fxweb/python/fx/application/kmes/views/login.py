"""
@file      kmes/views/login.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES login view
"""
from flask import request

from auth import ApiUser, User
from base.app_sanitize import validate_request_json_is_dict
from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from server_authentication import ServerAuthentication
from server_login_context import ServerLoginContext


class Login(ServerTranslatedView):
    decorators = [validate_request_json_is_dict]

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Login")

    def post(self):
        request_json = request.get_json(force=True)
        user_class = ApiUser if request_json.pop("_apiOnlySession", True) else User

        # Get the context for this user session, otherwise create a new one
        user = ServerAuthentication.get_current_user()
        if user:
            success, context = ServerLoginContext(self.server_interface).get_context(user)
        else:
            success, context = ServerLoginContext(self.server_interface).create_middleware_context()
            user = ServerAuthentication.make_user(context, user_class=user_class)

        if not success:
            return APIResponses.internal_error("Failed to connect to server.")

        # Send the API login to the server
        login_response = self.translate("Submit", (request_json, context))
        success, message = login_response.pop("success", False), login_response.pop("message", "")

        if not success:
            # Handle the case where we are already authenticated
            if message.find("already logged in") >= 0:
                return APIResponses.failure("Already logged in.")

            return APIResponses.unauthorized(message)

        frontend_response = APIResponses.success(message="Success", body=login_response)

        # Add CSRF for browser login
        if user.is_authenticated and user.requires_csrf:
            frontend_response.set_cookie(key="FXSRF-TOKEN", value=context.csrf_token)

        return frontend_response
