"""
@file      rk_host_application_server_interface.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2019

@section DESCRIPTION
A server interface to communicate with the Host API
"""

from typing import Any
from flask_login import current_user, logout_user
from flask import g


import lib.utils.hapi_parsers as parser
from auth import User
from middleware_context import MiddlewareContext
from lib.auth.credentials import JwtCredentials, PkiNonceCredentials, PkiSignatureCredentials, UserPassCredentials
from lib.utils.container_filters import filter_none_values
from lib.utils.fx_decorators import singledispatchmethod
from server_interface import ServerInterface
from connection_interface import ConnectionInterface
from connection_handler import MiddlewareConnectionHandler
from conn_exceptions import MissingConnectionException, NoSuchExcryptCommand
from command_factory import CommandFactory
from auth import token_authentication
from rk_login_status import LoginStatus, PkiNonceLoginDetails, UserRoleLoginDetails

class LoginResponseMessage:
    def __init__(self, resp=None):
        resp = {} if resp is None else resp

        self.success = resp.get('AN') == 'Y'
        self.auth_token = resp.get('JW', '')
        self.fully_logged_in = parser.parse_bool(resp.get('LN', '0'))
        self.pending_groups = parser.parse_csv(resp.get('AC', ''))
        self.authorized_groups = parser.parse_csv(resp.get('UG', ''))
        self.users_total = int(resp.get('UT', '0'))
        self.users_logged_in = int(resp.get('UL', '0'))

        self.pki_provider = resp.get('CN', '')
        self.pki_challenge_nonce = resp.get('BO', '')
        self.pki_session_id = resp.get('TH', '')
        self.pki_subject = resp.get('IC', '')

        # This isn't returned in the host API
        self.password_change = False

        # Parse the users into objects to match the rk_server_interface
        self.users = []
        user_ids = parser.parse_csv(resp.get('SD', ''))
        user_names = parser.parse_csv(resp.get('SU', ''))
        for uid, name in zip(user_ids, user_names):
            self.users.append({'id': uid, 'name': name})

        # Get the error and add a default one if none exists
        self.error = ''
        if not self.success:
            self.error = resp.get('BB', 'Could not get login response from server')


class RKHostApplicationServerInterface(ServerInterface):
    def __init__(self, program):
        super(RKHostApplicationServerInterface, self).__init__(program)
        self.program = program
        self.log = program.app_interface.log
        self.conn_handler = MiddlewareConnectionHandler(program.config)
        self.command_type = 'HAPI'
        self.jwt_pool = token_authentication.JWTContextPool(self)

    def connect(self, conn_context):
        return self.conn_handler.connect(conn_context)

    def _send(self, msg, context=None):
        response = None
        if context is None:
            context = current_user.context

        # Try to send a message
        try:
            response = self.conn_handler.send_synch(
                context,
                msg,
                ConnectionInterface.DEFAULT_TIMEOUT
            )
        except MissingConnectionException:
            raise

        return response

    def send(self, msg):
        jwt = getattr(g, 'jwt', None)
        if jwt is not None:
            return self.send_jwt(msg, jwt)
        else:
            return self._send(msg)

    def send_jwt(self, msg, token):
        with self.jwt_pool.acquire(token) as context:
            msg = context.add_to_request(msg, token)
            response = self._send(msg, context)
            context.update_from_response(response, token)
        return response

    # The translator and server communicate by consulting the command factory
    def send_command(self, category, name, request_data):
        result = {}
        command_instance = CommandFactory.get_command(
            command_type=self.command_type,
            command_category=category,
            command_name=name,
            server_interface=self
        )

        if command_instance is not None:
            result = command_instance.send(request_data)
        else:
            raise NoSuchExcryptCommand(cmd_name=name)

        return result

    def login_user(self, server_request):
        """
        Logs a user in, and ensures that all required users have been logged in before allowing
        access to web resources
        """
        login_data = server_request.data
        credentials = login_data.credentials
        context = login_data.context

        return self._login_user(credentials, context, login_now=login_data.login_now)

    @singledispatchmethod
    def _login_user(self, credentials: Any, context, **kwargs):
        # Fallback, shouldn't happen
        raise NotImplementedError('Unable to parse user credentials')

    @_login_user.register(PkiNonceCredentials)
    def _nonce_request_login(self, credentials: PkiNonceCredentials, context: MiddlewareContext,
                             **kwargs) -> LoginStatus:
        login_dict = filter_none_values({
            'CE': credentials.cert,
            'CT': credentials.cert_chain and ','.join(credentials.cert_chain) or None,
        })

        login_resp = LoginResponseMessage(self.send_command('User', 'RKLO', login_dict))

        login_status = self._parse_login_response(login_resp, context)
        login_status.login_details = PkiNonceLoginDetails(**vars(login_resp))

        return login_status

    @_login_user.register(JwtCredentials)
    def _nonce_request_login(self, credentials: JwtCredentials, context: MiddlewareContext,
                             **kwargs) -> LoginStatus:
        login_dict = filter_none_values({
            'HD': '1',  # Explicitly keep connection logged in
            'JW': credentials.token,
        })

        login_resp = LoginResponseMessage(self.send_command('User', 'RKLO', login_dict))

        login_status = self._parse_login_response(login_resp, context)
        login_status.login_details = UserRoleLoginDetails(**vars(login_resp))

        return login_status

    @_login_user.register(PkiSignatureCredentials)
    def _nonce_signature_login(self, credentials: PkiSignatureCredentials,
                               context: MiddlewareContext, **kwargs) -> LoginStatus:
        login_dict = {
            'HD': '1',  # Explicitly keep connection logged in
            'TH': credentials.session_id,
            'SI': credentials.signature,
        }
        login_resp = LoginResponseMessage(self.send_command('User', 'RKLO', login_dict))

        login_status = self._parse_login_response(login_resp, context)
        login_status.login_details = UserRoleLoginDetails(**vars(login_resp))

        return login_status

    @_login_user.register(UserPassCredentials)
    def _userpass_login(self, credentials: UserPassCredentials, context: MiddlewareContext,
                        login_now: bool, **kwargs) -> LoginStatus:
        login_dict = {
            'DA': credentials.username,
            'CP': credentials.hex_password,
            'LN': '1' if login_now else '0',
        }

        if credentials.old_password is not None:
            login_dict['OX'] = credentials.old_password

        login_resp = LoginResponseMessage(self.send_command('User', 'RKLO', login_dict))

        login_status = self._parse_login_response(login_resp, context)
        login_status.login_details = UserRoleLoginDetails(**vars(login_resp), login_now=login_now)

        return login_status


    def _parse_login_response(self, login_resp, context) -> LoginStatus:
        if not login_resp.success:
            return LoginStatus(
                success=False,
                login_message=login_resp.error,
            )

        # Construct a login_info upon success
        login_info = self._get_login_info(context, login_resp)

        # Construct the login status
        status = LoginStatus(
            success=login_resp.success,
            fully_logged_in=login_resp.fully_logged_in,
            password_change=login_resp.password_change,
            login_message=login_resp.error,
            login_info=login_info,
        )

        return status

    def _get_login_info(self, context, login_resp: LoginResponseMessage):
        """
        Helper method to generate a LoginInfo structure populated from the response
        :return: Returns a LoginInfo structure
        """
        login_info = {
            'id': login_resp.authorized_groups,
            'name': 'N/A',
            'permissions': [],
            'users': login_resp.users,
            'can_send_commands': bool(login_resp.authorized_groups),
        }

        context.login_info = login_info

        return login_info

    def logout_user(self):
        """
        Logs users out of the backend rkserver
        """
        try:
            # Remove the connection from the connection handler dict
            self.conn_handler.remove(current_user.context)
        except MissingConnectionException:
            # Ignore the error if the connection is already gone
            pass
        finally:
            if current_user is not None:
                # Remove the user session object and update the session cookie
                User.remove(current_user.get_id(), logout_user)
