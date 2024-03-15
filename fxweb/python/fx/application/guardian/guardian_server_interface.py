"""
@file      guardian_server_interface.py
@author    Tim Brabant(tbrabant@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
A server interface to interact with specifically with a Guardian backend.
"""

from flask_login import current_user

from app_matcher import DeleteObjectMatcher, UpdateObjectMatcher, NotifyExternalChangeMatcher
from base_exceptions import UserNotLoggedIn
from conn_exceptions import InvalidMessageException, MissingConnectionException
from rk_application_server_interface import RKApplicationServerInterface
from application_log import ApplicationLogger as Log
from listener import SocketIOObjectUpdateListener, SocketIOObjectDeleteListener, SocketIONotifyExternalChangeListener
from file_download import init_download_dir
from server_credentials import ServerLoginCredentials
from server_login_response import ServerLoginResponse
from rk_login_status import DEFAULT_LOGIN_REQUIRED, LoginStatus, LoginDetails
from rk_server_authentication import RKAuthStatus

from librk import (
    ExcryptMessage,
    ManagedObject
)

# Enum for CMD_REROUTING_TAG on rkserver's side
PEER_PORT_CMD_REROUTE_ENUM = 2

class GuardianServerInterface(RKApplicationServerInterface):
    """
        Guardian interface class. Implements CRUD operations
        when communicating with a backend Guardian rkserver.
    """
    socketio = None

    def __init__(self, program):
        super(GuardianServerInterface, self).__init__(program)
        self.guardian_initialization()
        self.rk_auth = RKAuthStatus()

    def guardian_initialization(self):
        """Initialization of the guardian server interface"""

        # TODO Move this into a SocketIO subclass view or something similar
        managers = ["CARDGROUP", "KMES_GROUP", "REMOTE_KEY_GROUP",
                    "CARD", "LOCAL_GUARDIAN_DEVICE", "GUARDIAN_DEVICE",
                    "KMES_DEVICE", "REMOTE_KEY_DEVICE",
                    "INDIVIDUAL_STAT", "AGGREGATE_STAT", "PEER", "EVENT", ]

        socketio = self.program.app_interface.socket
        self.conn_handler.add_message_listener(SocketIOObjectUpdateListener(
            UpdateObjectMatcher(managers), socketio))
        self.conn_handler.add_message_listener(SocketIOObjectDeleteListener(
            DeleteObjectMatcher(managers), socketio))
        self.conn_handler.add_message_listener(SocketIONotifyExternalChangeListener(
            NotifyExternalChangeMatcher(managers), socketio))

        init_download_dir()

    def _get_checksum_message(self, server_request):
        """Returns the message we send to backend to get major key checksums

        Arguments:
            server_request - frontend json request

        Returns:
            An ExcryptMessage with the backend request
        """
        object_type = server_request.get("objectType")

        checksums_command = self._get_hash_command(object_type)
        checksums_message = ExcryptMessage(checksums_command)

        if "LOCAL_GUARDIAN" not in server_request.get("objectType"):
            self._set_multi_balanced_device_info(
                server_request, checksums_message)

        return checksums_message

    def _get_checksum_tag_value(self, server_request, backend_response):
        """Retrieves the checksum tag value from the given backend response

        Arguments:
            server_request - frontend json request
            backend_response - backend ExcryptMessage response

        Returns:
            A string with the checksum tag's value
        """
        object_type = server_request.get("objectType")

        return backend_response.getField(self._get_hash_command_response_tag(object_type))

    def _get_hash_command(self, object_type):
        """Gets the hash command given the object type.

        Arguments:
            object_type {string} -- Object type.
        """

        if "CARD" in object_type or "LOCAL_GUARDIAN" in object_type:
            return "[AOSKEY;BJ9;]"
        else:
            return "[AORKHA;MF2;]"

    def _get_hash_command_response_tag(self, object_type):
        """Gets the hash command response tag given the object type.

        Arguments:
            object_type {string} -- Object type.
        """

        if "CARD" in object_type or "LOCAL_GUARDIAN" in object_type:
            return "AE"
        else:
            return "MK"

    def _get_formdata(self, request_type, request_values):
        """
        Helper method to get form data for an object
        """
        frontend_response = {}
        try:
            name = request_type.get('name')
            if name == "remote_login":
                login_data = request_values.get('login_data')

                frontend_response = self._remote_login(login_data)
            
            elif name == "remote_logout":
                logout_data = request_values.get('logout_data')

                frontend_response = self._remote_logout(logout_data)

        except (ValueError, KeyError):
            raise InvalidMessageException(None, "Could not parse request/response")
        except UserNotLoggedIn as exception:
            # Any operation could hit a timeout or other error that leaves us logged out.
            # Let the frontend know so they can handle it.
            frontend_response = {"result": "Failure", "reason": "No longer signed in."}
            self._deregister_authenticated_object_id(exception.user, exception.is_group, exception.object_id)

        return frontend_response

    def _remote_logout(self, logout_data):

        frontend_response = {}

        logout_command = self._get_logout_command(logout_data)
        logout_message = ExcryptMessage(logout_command)
        self._set_multi_balanced_device_info(logout_data, logout_message)

        is_group = self._is_routed_to_group(logout_data)
        is_card = self._is_routed_to_card(logout_data)

        try:
            # Send the logout command to the server.
            rsp_msg = ExcryptMessage(self.send(logout_message.getText()))
            self._deregister_authenticated_object_id(current_user, is_group,
                                                      logout_data.get("objectID"))

            # Cards do no respond with an AN tag for logouts.
            if rsp_msg and (rsp_msg.getField("AN") == "Y" or is_card):
                frontend_response = {
                    'result': 'Success',
                    'message': 'Logged out successfully.'
                }
            else:
                frontend_response = {
                    'result': 'Failure',
                    'message': 'Could not log out successfully.'
                }

        except MissingConnectionException:
            # Ignore the error if the connection is already gone
            raise

        return frontend_response

    def _remote_login(self, login_data):
        """
        Helper method to login to a remote device and store the fact that we did.
        """

        auth_credentials = login_data.get("auth_credentials")
        login_command = self._get_login_command(auth_credentials)
        login_message = ExcryptMessage(login_command)

        # Remote app devices will use this, cards will not.
        login_info_message = ExcryptMessage("[AORKY99;YB{};OA0;]".format(PEER_PORT_CMD_REROUTE_ENUM))

        server_login_credentials = ServerLoginCredentials.parse(login_data)
        login_message.setFieldAsString("DA", server_login_credentials.username)
        login_message.setFieldAsString("CH", server_login_credentials.password)

        self._set_multi_balanced_device_info(auth_credentials, login_message)
        self._set_multi_balanced_device_info(auth_credentials, login_info_message)

        login_status = self._login_to_remote(current_user.context, login_data,
                                              login_message.getText(), login_info_message.getText())

        full_auth, response = ServerLoginResponse.parse_credentials(login_status)

        return response

    def _login_to_remote(self, context, login_data, login_message, login_info_message):
        """
        Perform the actual server login
        Arguments:
            interface: The interface to interact with the server
            server_request: The message to send to the server
            context: The connection context
        Returns: Login status after server login
        """

        full_auth_creds = login_data.get("auth_credentials")
        object_id = full_auth_creds.get("objectID")
        session_ids = (object_id, full_auth_creds.get("objectParentID"))
        is_group = self._is_routed_to_group(full_auth_creds)

        # We might be signing into a group instead, in which case there
        # is no objectID field, just the parents'.
        if not object_id:
            object_id = full_auth_creds.get("objectParentID")

        auth_credentials = ServerLoginCredentials.parse(login_data)
        user = current_user
        login_status = None

        # Cards do not supply information on how many more users need to be logged in,
        # so we need to keep track ourselves with a different login path.
        if self._is_routed_to_card(full_auth_creds):
            login_status = self._login_card_user(context, auth_credentials, login_message, session_ids)
        else:
            login_status = self._login_app_user(context, auth_credentials, login_message, login_info_message)

        # Update the login status upon success
        def update(user, login_status):
            login_status.login_message = "All users have logged in."
            # Returns to the client that the user is fully logged in
            login_status.fully_logged_in = True
            self._register_authenticated_object_id(user, is_group, object_id)

        if login_status.success:
            login_status = self.rk_auth.update_auth_status(user, login_status, update)

        elif login_status.login_message == "ALREADY LOGGED IN":
            # The frontend might have presented a login button when we're already
            # logged in. Update and rebake the cookie.
            self._register_authenticated_object_id(user, is_group, object_id)

        return login_status

    def _login_card_user(self, context, credentials, login_message, session_ids):
        """
        Helper method to keep track of server login requests to cards and card groups.
        """
        # There's only one group on cards...
        login_info = {'name': 'Admin'}

        # Result data.
        success = False
        fully_logged_in = False
        users_total = DEFAULT_LOGIN_REQUIRED
        users_logged_in = 0
        server_error = ""

        # Send the command, get the response.
        em_resp = None
        try:
            resp = self.send(login_message, context=context)
            em_resp = ExcryptMessage(resp)

            success = em_resp.getFieldAsBool("CN", "Y")

            # The card does not supply information on how many more users are required to
            # login, so like RK we will assume it is 2 and keep track ourselves.
            if success:
                user = current_user
                already_authed_users = user.get_card_login_in_progress(session_ids)

                # Thus, if there is no active session, the first user just logged in...
                if not already_authed_users:
                    users_logged_in = 1
                    user.add_card_login_in_progress(session_ids, credentials.username)

                # ... and if there is, we're done with login.
                else:
                    if credentials.username in already_authed_users:
                        success = False
                        server_error = "User already logged in."
                    else:
                        user.remove_card_login_in_progress(session_ids)
                        users_logged_in = DEFAULT_LOGIN_REQUIRED
                        fully_logged_in = True

        except:
            success = False
            raise

        if not success and not server_error and em_resp:
            # Construct the error message
            bb_tag = em_resp.getField("BB") if em_resp.hasField("BB") else ""

            if not bb_tag:
                server_error = "Bad login attempt."
            else:
                server_error = bb_tag

        status = LoginStatus(success=success, fully_logged_in=fully_logged_in,
                             login_message=server_error, login_info=login_info)
        # HSM logins do not use user roles
        status.login_details = LoginDetails(users_total=users_total,
                                            users_logged_in=users_logged_in)
        return status

    def _is_routed_to_card(self, auth_credentials):
        """
        Are these credentials going to a card or card group?
        """
        return "CARD" in auth_credentials.get("objectType")

    def _get_login_command(self, auth_credentials):
        """
        Gets the correct login command for the given login credentials.
        """

        login_command = "[AORKY16;YB{};OA0;]".format(PEER_PORT_CMD_REROUTE_ENUM)

        if "CARD" in auth_credentials.get("objectType"):
            login_command = "[AOGUSR;]"

        return login_command

    def _get_logout_command(self, auth_credentials):
        """
        Gets the correct logout command for the given credentials.
        """

        logout_command = "[AORKY20;YB{};OA0;]".format(PEER_PORT_CMD_REROUTE_ENUM)

        if "CARD" in auth_credentials.get("objectType"):
            logout_command = "[AOGUSR;]"

        return logout_command

    def _register_authenticated_object_id(self, user, is_group, object_id):
        """
        Registers a device or group as authorized for a user.
        In other words, they've logged into it.
        """
        if is_group:
            user.authenticated_remote_groups.add(object_id)
        else:
            user.authenticated_remote_devices.add(object_id)

    def _deregister_authenticated_object_id(self, user, is_group, object_id):
        """
        Deregisters a device or group as authorized for a user.
        In other words, the connection timed out or they logged out.
        """
        try:
            if is_group:
                user.authenticated_remote_groups.remove(object_id)
            else:
                user.authenticated_remote_devices.remove(object_id)
        except KeyError:
            # If it didn't already exist in the sets, that's fine.
            pass

    def _add_whitelist(self):
        """ Gets allowed managed object types that can be added.
        Returns: A list of types that are allowed to be added.
        """
        return [
            ManagedObject.CARD,
            ManagedObject.CARDGROUP,
            ManagedObject.GUARDIAN_DEVICE,
            ManagedObject.GUARDIAN_GROUP,
            ManagedObject.KMES_DEVICE,
            ManagedObject.KMES_GROUP,
            ManagedObject.REMOTE_KEY_DEVICE,
            ManagedObject.REMOTE_KEY_GROUP,
        ]

    def _delete_whitelist(self):
        """ Gets allowed managed object types that can be deleted
        Returns: A list of types that are allowed to be deleted
        """
        return [
            ManagedObject.CARD,
            ManagedObject.CARDGROUP,
            ManagedObject.GUARDIAN_DEVICE,
            ManagedObject.GUARDIAN_GROUP,
            ManagedObject.KMES_DEVICE,
            ManagedObject.KMES_GROUP,
            ManagedObject.REMOTE_KEY_DEVICE,
            ManagedObject.REMOTE_KEY_GROUP,
        ]

    def _filter_whitelist(self):
        """ Gets allowed managed object types that can be filtered.
        Returns: A list of types that are allowed to be filtered.
        """
        return [
            ManagedObject.TYPE.CARD,
            ManagedObject.TYPE.CARDGROUP,
            ManagedObject.TYPE.EVENT,
            ManagedObject.TYPE.LOG,
            ManagedObject.TYPE.JOB,
            ManagedObject.TYPE.KMES_DEVICE,
            ManagedObject.TYPE.KMES_GROUP,
            ManagedObject.TYPE.GUARDIAN_DEVICE,
            ManagedObject.TYPE.GUARDIAN_GROUP,
            ManagedObject.TYPE.REMOTE_KEY_DEVICE,
            ManagedObject.TYPE.REMOTE_KEY_GROUP,
            ManagedObject.TYPE.PEER,
            ManagedObject.TYPE.LOG_FILTER,
            ManagedObject.TYPE.LOCAL_GUARDIAN_DEVICE,
            ManagedObject.TYPE.LOCAL_GUARDIAN_GROUP,
            ManagedObject.TYPE.INDIVIDUAL_STAT,
            ManagedObject.TYPE.AGGREGATE_STAT
        ]
