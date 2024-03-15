"""
@file      server_login_response.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Creates a response to a login request from the client
"""
from flask import jsonify
from js_encoding import json_uri_component

import fx
from rk_login_status import LoginStatus


class ServerLoginResponse(object):
    """Creates responses for login attempts """
    @staticmethod
    def has_no_credentials(login_status=None):
        """Handle an attempt to login without credentials
        Arguments:
            login_status: The result of the login attempt (empty)
        Returns:
            frontend_response: json message The frontend response and a LoginStatus
        """
        if login_status is None:
            login_status = LoginStatus()

        frontend_response = jsonify(result='Failure',
                                    message=login_status.login_message)
        return frontend_response, login_status

    @staticmethod
    def is_already_authenticated(login_status=None):
        """Handle an attempt to login when the user is already logged in
        Arguments:
            login_status: The result of the login attempt (empty)
        Returns: The frontend response and a LoginStatus
        """
        if login_status is None:
            login_status = LoginStatus()

        frontend_response = jsonify(result=login_status.success,
                                    message="User already logged in.")
        return frontend_response, login_status

    @staticmethod
    def has_credentials(context, login_status):
        """Parse the login status from a login attempt
        Arguments:
            context: The user's context
            login_status: The result of the login attempt
        Returns: The frontend response and a LoginStatus
        """
        # Generate the web client response
        full_auth, response = ServerLoginResponse.parse_credentials(login_status)
        frontend_response = jsonify(**response)

        # Fully logged in
        if full_auth:
            # Set the CSRF cookie
            frontend_response.set_cookie(key='FXSRF-TOKEN', value=context.csrf_token, samesite='Strict', secure=True)

        return frontend_response, login_status

    @staticmethod
    def parse_credentials(login_status):
        """Parse the login status for a login attempt
        Arguments:
            login_stats: The result of the login attempt
        Returns:
            full_auth: if the connection is fully logged in
            response: containing a dictionary of key value pairs
        """
        response = dict(
            login_message=login_status.login_message
        )

        # Login status should contain details about a login response
        if login_status.login_details is not None:
            # Default login
            response['total_required'] = login_status.login_details.users_total
            response['total_logged_in'] = login_status.login_details.users_logged_in

            # User role login
            if login_status.login_details.has_user_role_details():
                response['pending_groups'] = login_status.login_details.pending_groups
                response['authorized_groups'] = login_status.login_details.authorized_groups

        # Determine whether to include the "login_info" and the value of "result"
        success = login_status.success
        full_auth = success is True and login_status.fully_logged_in is True
        if full_auth:
            response['result'] = success
            response['login_info'] = login_status.login_info
        else:
            response['result'] = 'Success' if success else 'Failure'

        return full_auth, response
