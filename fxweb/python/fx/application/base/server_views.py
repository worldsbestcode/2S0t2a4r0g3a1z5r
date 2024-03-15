"""
@file      server_views.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Base Views implementation that abstracts out URI to server interface implementation
"""

from flask import request, jsonify, redirect, url_for, make_response
from flask_login import current_user, logout_user
import jsonschema
import urllib

import fx
from fx_view import FxView
from server_request import ServerRequest
from rk_login_status import LoginStatus
from static_content_view import StaticContentView, create_static_response
from auth import User, token_authentication, rkweb_session, rkweb_sync
from utils.response_generator import APIResponses
from app_sanitize import sanitize_request, validate_request_json_is_dict
from form_view import FormView
from app_csrf import csrf_required
from server_authentication import ServerAuthentication
from server_credentials import ServerLoginCredentials
from server_login_context import ServerLoginContext
from server_login_response import ServerLoginResponse
from translator_factory import TranslatorFactory

class ServerDefaultView(FxView):
    """
    The default view to redirect to login
    """

    def __init__(self, server_interface):
        super(ServerDefaultView, self).__init__(server_interface)

    def get(self, *args, **kwargs):
        """
        Redirects to the login page
        """
        frontend_response = redirect("/")
        frontend_response.headers['Cache-Control'] = 'no-cache'
        return frontend_response

    @staticmethod
    def _is_current_authed():
        return ServerAuthentication.is_current_authed()

    @staticmethod
    def _authenticated(user):
        return ServerAuthentication.authenticated(user)

    @staticmethod
    def _get_current_user():
        return ServerAuthentication.get_current_user()


class ServerTranslatedView(FxView):
    """
    This view uses translators to talk to the server
    """
    decorators = [token_authentication.jwt_optional, validate_request_json_is_dict]

    def __init__(self, server_interface, translator_type, translator_category):
        super(ServerTranslatedView, self).__init__(server_interface)
        self.translator_type = translator_type
        self.translator_category = translator_category

    def translate(self, operation, request_data, *, translator_category=None):
        result = {}

        translator_class = TranslatorFactory.get_translator(
            self.translator_type,
            translator_category or self.translator_category,
            operation
        )

        if translator_class is not None:
            translator_instance = translator_class(self.server_interface)
            result = translator_instance.translate(request_data)

        return result


class ServerLoginView(ServerDefaultView):
    """
    The login view to handle logging into a back end server
    """
    decorators = [sanitize_request]

    def __init__(self, server_interface):
        super(ServerLoginView, self).__init__(server_interface)
        self._response = ServerLoginResponse
        self._context = ServerLoginContext(server_interface)
        self._auth = ServerAuthentication(server_interface)

    def post(self, *args, **kwargs):
        """
        Performs the login action
        """
        login_data = request.get_json()
        frontend_response, _ = self._login(login_data)
        return frontend_response

    def _login(self, login_data):
        """Performs login to backend server
        Arguments:
            login_data: Holds client request data that contains login info
        Returns: a response based on authentication status
        """
        credentials = self._credentials(login_data)
        user = self._get_current_user()
        if self._authenticated(user):
            return self._response.is_already_authenticated()
        elif credentials is not None:
            # Login tracking data
            login_status = self.__internal_login(user, credentials, login_data)
            return self._has_credentials(login_status)
        else:
            return self._response.has_no_credentials()

    def __internal_login(self, user, credentials, client_request):
        """
        Internal login method that performs login to backend, and updates middleware bookkeeping
        :param user: Current User object
        :param credentials: Object containing current credential set
        :param request: Request object received from web client
        :return: Returns login status
        """
        login_status = LoginStatus()
        if user is None:
            login_status.success, context = self._context.create_middleware_context()
            user = self._auth.make_user(context)
        else:
            login_status.success, context = self._context.get_context(user)

        # If we generated or found the existing context, send the login command to the backend server
        if login_status.success:
            server_request = self._auth.login_request(context, credentials, client_request)
            login_status = self._auth.server_login(server_request, context)

        return login_status

    def _credentials(self, login_data):
        """Wrapper around ServerLoginCredentials.parse
        Arguments:
            login_data: The PUT credentials from the client
        Returns: A credential object
        """
        return ServerLoginCredentials.parse(login_data)

    def _has_credentials(self, login_status):
        """Wrapper around response for has credentials
        Arguments:
            login_status: the result of the login attempt
        Returns: A response, login_status pair
        """

        # Get current user's context
        user = self._get_current_user()
        success, context = self._context.get_context(user)

        return self._response.has_credentials(context, login_status)


class ServerLoginInfoView(ServerDefaultView):
    """
    Retrieve login status. Must be logged in to use this endpoint
    """
    decorators = [csrf_required]

    def __init__(self, server_interface):
        super(ServerLoginInfoView, self).__init__(server_interface)

    def get(self, *args, **kwargs):
        """Retrieves information about the current authorization state
        :return response with JSON
        """
        result = {}

        # Get the fxweb login state
        fxweb_user = self._get_current_user()
        context = fxweb_user.context
        # Special handling for anonymous
        if context and context.is_anonymous():
            result = {
                'id': fxweb_user.user_group_id,
                'name': 'Anonymous',
                'users': ['Anonymous'],
                'primaryIdentity': {
                    'id': 1001,
                    'name': 'Anonymous',
                },
                'permissions': context.login_info.get('permissions'),
            }
        # Output rkweb login info
        else:
            # Get rkweb session
            auth_sess = rkweb_session()

            # Convert perms to cat:perm dict format
            perms = {}
            for perm in auth_sess.perms:
                colpos = perm.find(":")
                if colpos != -1:
                    category = perm[0:colpos]
                    subperm = perm[colpos+1:]
                else:
                    category = perm
                    subperm = None

                if not category in perms:
                    perms[category] = []

                if subperm:
                    perms[category].append(subperm)

            # Get user name list
            users = []
            primaryuser = {}
            for user in auth_sess.users:
                users.append(user['name'])
                if not 'name' in primaryuser or user['name'] < primaryuser['name']:
                    primaryuser['id'] = user['id']
                    primaryuser['name'] = user['name']

            # Get logged in role information
            roleid = -1
            rolename = ''
            for role in auth_sess.roles:
                if not role['principal']:
                    continue
                roleid = role['id']
                if len(rolename) > 0:
                    rolename += ","
                rolename += role['name']

            # JSON output
            result = {
                'permissions': perms,
                'users': users,
                'id': roleid,
                'name': rolename,
                'primaryIdentity': primaryuser,
            }
        ret = APIResponses.get_success(body=result)
        ret.set_cookie("authed_ids",
                        urllib.parse.quote(fxweb_user.get_authed_ids_cookie()))
        return ret


class ServerLogoutView(FxView):

    def __init__(self, server_interface):
        super(ServerLogoutView, self).__init__(server_interface)

    def _logout(self):
        """
        Performs the logout action
        """
        # Logout the user from the backend server
        self.server_interface.logout_user()

        if current_user is not None:
            # Remove the user session object and update the session cookie
            User.remove(current_user.get_id(), logout_user)

    def get(self, *args, **kwargs):
        self._logout()
        # Redirect the client to login page
        frontend_response = redirect("/")
        frontend_response.headers['Cache-Control'] = 'no-cache'
        return frontend_response


class ServerObjectView(FxView):
    decorators = [sanitize_request, csrf_required]

    def __init__(self, server_interface):
        super(ServerObjectView, self).__init__(server_interface)
        # TODO find out what should go in schema and resolver
        self.schema = None
        self.resolver = None

    def post(self, *args, **kwargs):
        """
        Sends a filter request to the server and retrieves all objects requested by the filter
        """
        post_data = request.get_json()

        frontend_response = {}
        if post_data["method"] == "create":
            frontend_response = self.server_interface.create(ServerRequest(request, post_data["objectData"]))
        elif post_data["method"] == "validate":
            frontend_response = self.server_interface.validate(ServerRequest(request, post_data["objectData"]))
        else:
            frontend_response = self.server_interface.retrieve(ServerRequest(request, None))

        result = 'Failure'
        message = 'Could not {} objects'.format(post_data['method'])
        if frontend_response:
            result = frontend_response.get('result', 'Success')
            message = frontend_response.get('message', message)

        if result == 'Failure':
            return jsonify(result=result, message=message)

        return jsonify(result=result, objectData=frontend_response)

    def put(self, *args, **kwargs):
        put_data = request.get_json()

        frontend_response = None
        try:
            frontend_response = self.server_interface.update(ServerRequest(request, put_data["objectData"]))
        except:
            raise

        return jsonify(result="Success" if frontend_response else "Failure")

    def delete(self, *args, **kwargs):
        """
        Updates the backend server with object updates
        """
        delete_data = request.get_json()

        frontend_response = None
        try:
            frontend_response = self.server_interface.delete(ServerRequest(request, delete_data["objectData"]))
        except:
            raise

        if not frontend_response:
            return jsonify(result='Failure', message='Could not delete object')

        return jsonify(result='Success', objectData=frontend_response)

    def _validate_json(self, data):
        """
        Validates input json data
        """
        data_list = data if isinstance(data, list) else [data]
        for d in data_list:
            jsonschema.validate(data_list, self.schema, resolver=self.resolver)

        return True


class ServerAppView(FormView):
    """
    The landing page
    """
    def __init__(self, server_interface):
        super(ServerAppView, self).__init__(server_interface, "/landing.html")


class ServerFormDataView(FxView):
    """
    Controls access to form data requested by the client
    """
    decorators = [sanitize_request, csrf_required]

    request_types = [
        {}
    ]

    def __init__(self, server_interface):
        super(ServerFormDataView, self).__init__(server_interface)

    def post(self, *args, **kwargs):
        """
        Retrieve form data
        """
        post_data = request.get_json()
        frontend_response = {}

        if post_data["method"] == "retrieve":
            frontend_response = self.server_interface.formdata(
                ServerRequest(request, post_data["formData"]),
                self.request_types
            )

        return jsonify(result="Success" if frontend_response else "Failure", formData=frontend_response)
