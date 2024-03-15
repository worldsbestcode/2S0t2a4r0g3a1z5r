"""
@file      kmes/translators/login.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators defined for the Login method view
"""
import json
from base64 import b64decode

from base.base_translator import BaseTranslator
from kmes.schemas import login as LoginSchemas
from server_authentication import ServerAuthentication
from server_credentials import ServerLoginCredentials


class LoginSubmit(BaseTranslator):

    request_schema = LoginSchemas.SubmitLogin()

    _output_type = dict  # we want our translated result to be a nested dict, not an ExcryptMessage

    def __init__(self, server_interface):
        request_map = {
            "authType": "auth_type",
            "_loginNow": ("login_now", bool),
            "authCredentials.username": "auth_credentials.username",
            "authCredentials.password": ("auth_credentials.password", b64decode),
        }
        response_map = {
            "success": "success",
            "login_message": "message",
            "login_details.pending_groups": "pendingGroups",
            "login_details.authorized_groups": "authorizedGroups",
            "login_details.users_logged_in": ("totalLoggedIn", int),
            "login_details.users_total": ("totalRequired", int),
            "fully_logged_in": ("loginComplete", bool),
            "login_info.users": ("loggedInUsers", lambda users: [user["name"] for user in users]),
        }
        super(LoginSubmit, self).__init__(server_interface, None, None, request_map, response_map)

    def translate(self, request):
        request, self.context = request
        return super(LoginSubmit, self).translate(request)

    def makeRequest(self, request):
        # Override to use RKApplicationServerInterface.login_user instead of send_command

        # Put the request dict into a ServerRequest object
        server_request = ServerAuthentication.login_request(
            context=self.context,
            request_object=request,
            credentials=ServerLoginCredentials.parse(request),
        )
        # Try to login, and get back a LoginStatus
        response = ServerAuthentication(self.server_interface).server_login(server_request, None)

        # Make a nested dict from the attributes of the LoginStatus for response_map translation
        return json.loads(json.dumps(response, default=vars))
