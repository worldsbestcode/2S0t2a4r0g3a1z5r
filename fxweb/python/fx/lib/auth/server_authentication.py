"""
@file      server_authentication.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Performs functions needed to login to the remotekey server
"""
from collections import namedtuple
from flask import session, request
from flask_login import current_user, login_user

import fx
from auth import User, ApiUser, SecurusUser
from rk_login_status import LoginStatus
from server_request import ServerRequest
from rk_server_authentication import RKAuthStatus
from rkweb.security import ClientType, get_client_type

class LoginData:
    """Login Request Data"""
    def __init__(self, context, credentials, json_login_data):
        """
        Arguments:
            context: The connection created for this login
            credentials: Parse credentials from the message
            login_now: If true login immediately
        """
        self.context = context
        self.credentials = credentials
        self.login_now = json_login_data.get('login_now', False)


class ServerAuthentication(object):
    """Methods for handling authentication and login of user"""
    def __init__(self, server_interface):
        """Initialize the authentication with a server interface"""
        self.interface = server_interface
        self.rk_auth = RKAuthStatus()

    def server_login(self, server_request: ServerRequest, context) -> LoginStatus:
        """Perform the actual server login
        Arguments:
            server_request: The message to send to the server
            context: The connection context
        Returns: Login status after server login
        """
        login_status = self.interface.login_user(server_request)
        if login_status.success:
            user = self.get_current_user()
            login_status = self.rk_auth.update_auth_status(user, login_status)

        return login_status

    @staticmethod
    def authenticated(user):
        """If the user is logged in or not Anonymous users are never authenticated"""
        return user is not None and user.is_authenticated

    @staticmethod
    def login_request(context, credentials, request_object):
        """Construct a server_request for login
        Arguments:
            context: connection context
            credentials: The login credentials
            request_object: The request object from the client
        Returns: server_request containing login request
        """
        login_data = LoginData(
            context,
            credentials,
            request_object,
        )
        server_request = ServerRequest(request_object, login_data)
        return server_request

    @staticmethod
    def get_current_user():
        """Return the current user if the session is still valid
        :return: The current user or none
        """
        if current_user is None:
            return None

        return User.get(current_user.get_id())

    @staticmethod
    def is_current_authed():
        """Convenience function to check authentication of current_user
        Returns: True if current_user is authenticated false otherwise
        """
        user = ServerAuthentication.get_current_user()
        return ServerAuthentication.authenticated(user)

    @staticmethod
    def make_user(context, user_class=None):
        """Creates and logs in a new user to the middleware session
        Arguments:
            context: the middleware connection context
            user_class: the type of user to create
        Returns: the new user
        """
        def deduce_user_type():
            client_type = get_client_type()
            if client_type == ClientType.ApiUser:
                return ApiUser
            if client_type == ClientType.Securus:
                return SecurusUser
            return User  # regular web browser user

        if not user_class:
            user_class = deduce_user_type()

        new_user = user_class()
        new_user.set_info(context)
        # Add the user to the logged in user list
        User.add(new_user)

        # Update the session cookie with a valid session id
        login_user(new_user)

        # Make this user adhere to timed sessions(Timeout after 60 minutes for now)
        session.permanent = True
        return new_user
