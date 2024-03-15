"""
@file      rk_application_server_interface.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
A server interface to interact with RKServer backends
"""
import json
import binascii
from collections import defaultdict

from flask import g
from flask_login import current_user, logout_user

from application_log import ApplicationLogger as Log
from conn_exceptions import InvalidMessageException
from connection_interface import ConnectionInterface
from connection_handler import MiddlewareConnectionHandler
from rk_login_status import DEFAULT_LOGIN_REQUIRED, LoginStatus, LoginDetails, UserRoleLoginDetails
from server_interface import ServerInterface
from app_matcher import QueryMatcher, DeleteObjectMatcher
from auth import Credentials, token_authentication, User
from conn_exceptions import MissingConnectionException, InvalidExcryptMessage, NoSuchExcryptCommand
from command_factory import CommandFactory
from rk_exceptions import (
    ObjectActionException,
    ObjectNotAddedException,
    ObjectNotDeletedException,
    ObjectNotModifiedException,
    ObjectNotValidatedException,
    ObjectNotFilteredException
)

import librk
from librk import (
    client,
    ExcryptMessage,
    Filter,
    ManagedObjectUtils,
    ManagedObject,
    MOAction
)


class RKApplicationServerInterface(ServerInterface):
    """
        RK Server Interface class. Implements CRUD operations
        when communicating with a backend rkserver.
    """

    def __init__(self, program):
        super(RKApplicationServerInterface, self).__init__(program)
        self.program = program
        self.log = program.app_interface.log
        self.conn_handler = MiddlewareConnectionHandler(program.config)
        self.command_type = 'HAPI'
        self.jwt_pool = token_authentication.JWTContextPool(self)

    def connect(self, conn_context):
        """ Opens a connection to the server"""
        return self.conn_handler.connect(conn_context)

    def _send(self, msg, matcher=None, context=None):
        """ Helper method to send data to connection associated with current context"""

        response = None
        conn_context = context if context is not None else current_user.context

        try:
            response = self.conn_handler.send_synch(
                conn_context,
                msg,
                ConnectionInterface.DEFAULT_TIMEOUT,
                matcher
            )
        except MissingConnectionException:
            raise

        return response

    def send(self, msg, matcher=None, context=None):
        jwt = getattr(g, 'jwt', None)
        if jwt is not None:
            return self.send_jwt(msg, jwt, matcher)
        else:
            return self._send(msg, matcher, context)

    def send_jwt(self, msg, token, matcher=None):
        with self.jwt_pool.acquire(token) as context:
            msg = context.add_to_request(msg, token)
            response = self._send(msg, matcher, context)
            context.update_from_response(response, token)
        return response

    def send_dict(self, field_tags, matcher=None, context=None):
        """Helper method for sending messages
        Arguments:
            field_tags: A dictionary containing tag/field pairs
            matcher: Message matcher forwarded to send
            context: Message context forwarded to send
        Returns: response as an excrypt message
        """
        try:
            # To make the command easier to spot we put it first
            cmd = field_tags.pop('AO')
        except KeyError:
            raise InvalidExcryptMessage('No command tag given')

        message = ExcryptMessage('[AO{};]'.format(cmd))
        for tag, field in field_tags.items():
            message.setFieldAsString(tag, field)

        message = message.getText()
        try:
            response = self.send(message, matcher, context) if message else ''
        except MissingConnectionException:
            raise

        return ExcryptMessage(response)

    def send_command(self, category, name, request_data):
        """
        Helper method for sending translated commands

        The translator and server communicate by consulting the command factory.
        """
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

    def convert_message(self, message, tag_names, tuple_type):
        """Helper for converting an excrypt message into a named tuple
        Arguments:
            message: The message to convert
            tag_names: An excrypt key name value dictionary
            tuple_type: The response type
        Returns: A tuple mapped to the values
        """
        response = {}
        for tag, name in tag_names.items():
            response[name] = message.getField(tag)

        return tuple_type(**response)

    def login_user(self, server_request):
        """
        Logs a user in, and ensures that all required users have been logged in before allowing
        access to web resources
        """
        request_data = server_request.request
        login_data = server_request.data
        credentials = login_data.credentials

        # User wants to login now without any further credentials (user role login)
        if request_data and 'login_now' in request_data and request_data['login_now']:
            login_message = "[AORKY16;LN1;UR1;]"

        # User has provided additional credentials
        else:
            if credentials.cred_type == Credentials.UserPass:
                pass_hex = credentials.hex_password
                login_message = "[AORKY16;DA{0};CP{1};]".format(credentials.username, pass_hex)
            elif credentials.cred_type == Credentials.Anonymous:
                login_message = "[AORKY106;OA0;]"
            elif credentials.cred_type == Credentials.Jwt:
                login_message = "[AORKY16;JW{0};HD1;]".format(credentials.token)

        login_info_message = "[AORKY99;OA0;]"

        return self._login_app_user(login_data.context, login_data.credentials, login_message, login_info_message)

    def _login_app_user(self, context, credentials, login_message, login_info_message):
        """
        Helper method to keep track of server login requests
        """
        # Results from RKY99
        login_info = {}

        # Results from RKY16
        success = False
        fully_logged_in = False
        server_error = ""

        # Default login data (RKY16 default response)
        users_total = DEFAULT_LOGIN_REQUIRED
        users_logged_in = 0

        # User role login data (RKY16 user role response)
        has_user_roles = False
        login_now = False
        pending_groups = []
        authorized_groups = []

        # Send the command, get the response
        em_resp = None
        try:
            em_req = ExcryptMessage(login_message)

            # User wants to login now without any further credentials (user role login)
            if em_req.hasField("LN"):
                resp = self.send(login_message, context=context)
                em_resp = ExcryptMessage(resp)

                success = fully_logged_in = em_resp.getFieldAsBool("LN", "1")
                has_user_roles = login_now = True

                if success and has_user_roles:
                    pending_groups, authorized_groups = self._get_user_roles(em_resp)

            # User has provided additional credentials
            else:
                # Username and password login
                if credentials.cred_type in [Credentials.UserPass, Credentials.Jwt]:
                    resp = self.send(login_message, context=context)
                    em_resp = ExcryptMessage(resp)

                    success = em_resp.getFieldAsBool("AN", "Y")
                    has_user_roles = em_resp.hasField("AC") and em_resp.hasField("UG")

                    if success:
                        # Handle default login response
                        users_total = em_resp.getFieldAsInt("UT")
                        users_logged_in = em_resp.getFieldAsInt("UL")

                        # Handle "user role" login response
                        if has_user_roles:
                            pending_groups, authorized_groups = self._get_user_roles(em_resp)

                # Anonymous login
                elif credentials.cred_type == Credentials.Anonymous:
                    resp = self.send(login_message, context=context)
                    em_resp = ExcryptMessage(resp)

                    success = em_resp.getFieldAsBool("AN", "Y")
                    has_user_roles = False

                    if success:
                        users_total = 1
                        users_logged_in = 1
                        fully_logged_in = True

        except:
            success = False
            raise

        # Determine the result
        if success is True:
            login_info = self._get_login_info(context, login_info_message)
        elif em_resp:
            # Construct the error message
            bb_tag = em_resp.getField("BB") if em_resp.hasField("BB") else ""
            er_tag = " - " + em_resp.getField("ER") if em_resp.hasField("ER") else ""

            default_error = "Could not get login response from server."

            # Determine which error message to use
            if len(bb_tag) + len(er_tag) > 0:
                server_error = bb_tag + er_tag
            else:
                server_error = default_error

        # Construct the login status
        status = LoginStatus(success=success, fully_logged_in=fully_logged_in,
                             login_message=server_error, login_info=login_info)
        if has_user_roles:
            status.login_details = UserRoleLoginDetails(
                users_total=users_total,
                users_logged_in=users_logged_in,
                pending_groups=pending_groups,
                authorized_groups=authorized_groups,
                login_now=login_now
            )
        else:
            status.login_details = LoginDetails(users_total=users_total,
                                                users_logged_in=users_logged_in)
        return status

    def _get_user_roles(self, em_resp):
        pending_groups_str = ''
        authorized_groups_str = ''

        pending_groups = []
        authorized_groups = []

        if em_resp.hasField("AC"):
            pending_groups_str = em_resp.getField("AC")
        if em_resp.hasField("UG"):
            authorized_groups_str = em_resp.getField("UG")

        if pending_groups_str != '':
            pending_groups = pending_groups_str.split(',')
        if authorized_groups_str != '':
            authorized_groups = authorized_groups_str.split(',')

        return pending_groups, authorized_groups

    def get_relevant_perms(self, perms, relevant_perms):
        """
        Helper method to get only the relevant permissions
        """
        result = defaultdict(lambda: [])
        for relevant_perm in relevant_perms:
            for perm in perms:
                if relevant_perm in perm:
                    cls, *_type = perm.split(":")

                    perm_flag = _type[0] if _type else cls
                    if perm_flag in result[cls]:
                        continue

                    result[cls].append(perm_flag)

        return result

    def _get_login_info(self, context, login_info_message):
        """
        Helper method to get the login group info from the backend rkserver
        :return: Returns a LoginInfo structure
        """
        group_name = "N/A"
        group_id = -1
        user_ids = []
        user_names = []
        relevant_perms = set(('CertManage', 'RequestApproval'))
        try:
            # Get auth status, auth only is false
            resp = self.send(login_info_message, context=context)
            em_resp = ExcryptMessage(resp)
            pending_groups, authorized_groups = self._get_user_roles(em_resp)
            json_resp = json.loads(binascii.a2b_base64(em_resp.getField("JA")))
            roles = [role for role in json_resp['roles']
                     if role['name'] in authorized_groups
                     or role['type'] == 'Anonymous']
            base_role = json_resp['baseRole']

            identities = json_resp['identities']
        except:
            raise

        # DBIDs don't fit in a JS number (64 vs 53 bits) so convert to str
        users = []
        for user in identities:
            users.append({'id': str(user['id']), 'name': user['name']})

        # Set name and id to authorized role with highest number of permissions
        active_role = max(roles, key=lambda role: len(role['perms']), default=base_role)
        role_name = active_role['name']
        role_id = str(active_role['id'])

        permissions = base_role['perms']
        for role in roles:
            permissions.extend(role['perms'])

        permissions = self.get_relevant_perms(permissions, relevant_perms)
        login_info = {
            'name': role_name,
            'id': role_id,
            'permissions': permissions,
            'users': users
        }
        context.login_info = login_info
        return login_info

    def logout_user(self):
        """
        Logs users out of the backend rkserver
        """
        try:
            # Send the logout command to the server
            self.send("[AORKY20;]")
            # Remove the connection from the connection handler dict
            self.conn_handler.remove(current_user.context)
        except MissingConnectionException:
            # Ignore the error if the connection is already gone
            raise
        finally:
            if current_user is not None:
                # Remove the user session object and update the session cookie
                User.remove(current_user.get_id(), logout_user)

    def query_rk_filter(self, filter, context, matcher=None, sync=True):
        """
        Query filter to rkserver. Will convert a Filter object to an Excrypt message and request the response from the
        server
        :param filter: A Filter object to create the message from
        :param context: The user context
        :param matcher: The response matcher
        :param sync: If true enable the PRESERVE_SYNC_RESP flag
        :return: A list of responses
        """
        if matcher is None:
            matcher = QueryMatcher(self._get_filter_manager_list(filter),
                                   context.get_resp_synch_tag(),
                                   context.inc_synch_value())

        if not self._all_filter_types_allowed(matcher.get_manager()):
            raise InvalidMessageException

        message = matcher.init_match_status(["ST", "[AORKY12;]"])

        em_request = ExcryptMessage(message)

        # Always force system objects excluded
        filter.setFlag(Filter.SYSTEM_EXCLUDE)
        if sync:
            filter.setFlag(Filter.PRESERVE_SYNC_RESP)
        filter.toMessage(em_request)

        # Send the filter
        try:
            responses = self.send(em_request.getText(), matcher)
        except MissingConnectionException:
            raise

        # Always return a list even if only one response matched
        if isinstance(responses, (bytes, str)):
            responses = [responses]

        Log.info('Returning %d objects from a filter for type %s' % (
            len(responses) - 1,  # Number of RKY400's - one required RKY12
            str(filter.getManager()),
        ))

        return responses

    def query_rk_associated_objects(self, primary, secondary, object_id, context, match_secondary_manager=True):
        """
        Query filter to rkserver. Will convert a Filter object to an Excrypt message and request the response from the
        server
        :param filter: A Filter object to create the message from
        :return: A list of responses
        """
        matcher = QueryMatcher(
            [secondary],
            context.get_resp_synch_tag(),
            context.inc_synch_value(),
            "RKY78",
            match_manager=match_secondary_manager)
        message = matcher.init_match_status(["ST", "[AORKY78;]"])

        em_request = ExcryptMessage(message)
        em_request.setFieldAsString("MN", str(int(primary)))
        em_request.setFieldAsString("MM", str(int(secondary)))
        em_request.setFieldAsString("ID", str(object_id))
        em_request.setFieldAsString("RS", "1")

        # Send the query
        try:
            responses = self.send(em_request.getText(), matcher)
        except MissingConnectionException:
            raise

        Log.info("Returning %d %s objects associated with %d %s objects" % (
            object_id.count(',') + 1 if object_id else 0,
            str(secondary),
            len(responses) - 1,  # number of optional RKY400's - one required RKY78
            str(primary),
        ))

        return responses

    def sync_manager(self, manager, num_responses=1):
        """
        Sends the sync manager request to the server
        :param manager: Manager to sync with from server
        :param num_responses: Number of responses to expect
        :return: Messages representing objects
        """
        matcher = QueryMatcher([manager], '', '')

        command = '[AORKY1;MN{};]'.format(manager)
        message = matcher.init_match_status(command)

        try:
            responses = self.send(command, matcher)
        except MissingConnectionException:
            raise

        return responses

    def delete_object(self, manager, dbid):
        """
        Send delete command to rkserver. This special method is used because rkserver doesn't use context tags(yet) for delete responses
        :param manager: Name of manager to delete from
        :param dbid: DBID of object to delete
        :return: A list of responses
        """
        # TODO In the future, modify this so that we context match results up until the RKY4 response is received
        matcher = DeleteObjectMatcher([manager], dbid)

        em_request = ExcryptMessage()
        em_request.setFieldAsString("AO", "RKY3")
        em_request.setFieldAsString("MN", manager)
        em_request.setFieldAsString("ID", dbid)

        msg = em_request.getText()
        # Send the command
        try:
            responses = self.send(msg, matcher, current_user.context)
        except MissingConnectionException:
            raise

        return responses

    def check_permission(self, manager, ids, action):
        """Check a specific object permission
        Arguments:
            mo_type: The managed object type
            ids: A list of object ids
            action: The object action to check
        Returns: The filter result
        """
        perm_filter = Filter()
        perm_filter.setManager(manager)
        perm_filter.setIDs(ManagedObjectUtils.getType(manager), ','.join(ids))
        perm_filter.setFilterType(Filter.COUNT)
        perm_filter.setPermFromAction(action)
        result = self.query_rk_filter(perm_filter, current_user.context)
        return result

    def _get_filter_manager_list(self, filter):
        """
        Helper method to populate expected manager types for filter
        based on filter flags
        """
        mo_type = ManagedObjectUtils.getType(filter.getManager())
        manager_list = [mo_type]
        if mo_type == ManagedObject.TYPE.APPROVABLE_OBJ:
            manager_list = [
                ManagedObject.TYPE.SIGNABLE_OBJ,
                ManagedObject.TYPE.CERT_REQ
            ]

        if filter.getFlag(Filter.DESCENDANTS):
            manager_list.append(ManagedObjectUtils.getChildType(mo_type))

        if filter.getFlag(Filter.ANCESTORS):
            manager_list.append(ManagedObjectUtils.getParentType(mo_type))

        return manager_list

    def retrieve(self, server_request):
        """
        Retrieve a batch of object(s) via a Filter request
        """
        # TODO Support batch objects
        request = server_request.request

        frontend_response = {}
        try:
            # Currently only supports single manager Filters
            # Build filter object from JSON
            filt = Filter()
            filt.fromJSONString(request.data, librk.eMOActionCreate)

            error = self._check_clauses(filt)
            if error:
                return dict(result='Failure', message=error)

            # Query server
            backend_response = self.query_rk_filter(filt, current_user.context)

            # Build response
            filterType = filt.getFilterType()
            filterManager = filt.getManager()
            if filterType == Filter.RESULTS:
                frontend_response = self._get_mos(filterManager, backend_response)
            elif filterType == Filter.COUNT:
                if isinstance(backend_response, (str, bytes)):
                    frontend_response = self._get_mo_count(filterManager, backend_response)
                else:
                    last_element = backend_response[len(backend_response)-1]
                    frontend_response = self._get_mo_count(filterManager, last_element)

        except (ValueError, IndexError, AttributeError) as e:
            Log.error('Failed to parse Filter results: %s' + str(e))
            raise InvalidMessageException(None, "Could not parse request/response")

        return frontend_response

    def create(self, server_request):
        """
        Creates an object on the remote server
        """
        # TODO Support batch objects

        frontend_response = self._add(server_request)

        return frontend_response

    def update(self, server_request):
        """
        Updates an object on the remote server
        """
        # TODO Support batch objects

        frontend_response = self._modify(server_request)

        return frontend_response

    def validate(self, server_request):
        """
        Performs server validation on object requests. Validates if input's for an object is correct
        """
        # TODO Support batch objects

        frontend_response = self._validate(server_request)

        return frontend_response


    def formdata(self, server_request, request_types, name):
        """
        Gets form data for an object
        """
        frontend_response = self._formdata(server_request, request_types, name)

        return frontend_response

    def delete(self, server_request):
        """
        Deletes object on remote server.
        Note: Currently not implemented because it is not used
        """
        frontend_response = self._delete(server_request)
        return frontend_response

    def get_monitored_ports(self):
        """
        Gets monitored ports from the server
        """
        message = "[AORKY59;]"

        # Send the command
        portscombined = ''
        try:
            response = self.send(message)
            em_response = ExcryptMessage(response)
            portscombined = em_response.getField("MP")
        except MissingConnectionException:
            raise

        # Remove empty values and convert to integers
        ports = [int(s) for s in portscombined.split(',') if s]
        frontend_response = {'ports': sorted(ports)}

        return frontend_response

    def _sanitize_object(self, mo):
        """
        Sanitize output objects
        Note: Currently unused
        """
        pass

    def _update_response(self, mo, response):
        """
        Helper method to update an object response to the web client
        """
        mo_name = ManagedObjectUtils.getManagerName(mo.getType())
        response.setdefault(mo_name, []).append(mo.toJSONString())

    def _update_delete_response(self, dbid, mo_name, response):
        """
        Helper method to update an object response for a delete request to the web client
        """
        response.setdefault(mo_name, []).append(dbid)

    def _add(self, server_request):
        """
        Internal add method. Deserializes json object, and serializes into EM. Sends add to remote server
        """
        frontend_response = {}
        add_types = self._add_whitelist()

        for k,v in server_request.data.items():
            for obj in v:
                try:
                    # Create managed object
                    mo_type = ManagedObjectUtils.getType(k)

                    if mo_type not in add_types:
                        raise ObjectNotAddedException(manager=mo_type, reason="object type is not allowed")

                    mo = ManagedObjectUtils.createObjectFromTypeTake(mo_type, 0)
                    if mo is not None:
                        # Deserialize into managed object
                        mo.fromJSONString(json.dumps(obj), librk.eMOActionCreate)

                        # Serialize into Excrypt message
                        em = ExcryptMessage()
                        mo.toMessage(em)
                        em.setFieldAsString("AO", "RKY2")
                        em.setFieldAsString("MN", k)

                        self._update_server(frontend_response, em, mo, True)

                except ObjectNotAddedException as exception:

                    Log.debug('Could not add requested object: {}'.format(obj))
                    raise

        return frontend_response

    def _modify(self, server_request):
        """
        Internal modify method. Deserializes json object, and serializes into EM. Sends modify to remote server
        """
        frontend_response = {}
        modify_types = self._modify_whitelist()

        for k,v in server_request.data.items():
            for obj in v:
                mo = None
                try:
                    # Create managed object
                    object_id = v[0]["objectID"]

                    if len(object_id) > 0:
                        mo_name = k
                        mo_type = ManagedObjectUtils.getType(mo_name)

                        if mo_type not in modify_types:
                            raise ObjectNotModifiedException(manager=mo_type, reason="object type is not allowed")

                        # Deserialize into managed object
                        filt = Filter()
                        filt.setManager(mo_name)
                        filt.setIDs(mo_type, object_id)

                        # Query server
                        backend_response = self.query_rk_filter(filt, current_user.context)

                        m = backend_response[0]
                        em = ExcryptMessage(m)
                        mo = ManagedObjectUtils.createObjectFromTypeTake(ManagedObject.TYPE(em.getFieldAsInt("TY")), 0)

                        if mo is not None:
                            mo.fromMessage(em)
                            mo.fromJSONString(json.dumps(obj), librk.eMOActionUpdate)
                            self._sanitize_object(mo)

                            # Serialize into Excrypt message
                            em = ExcryptMessage()
                            mo.toMessage(em)
                            em.setFieldAsString("AO", "RKY4")
                            em.setFieldAsString("MN", k)

                            # If update, update the object in the server
                            self._update_server(frontend_response, em, mo, False)
                        else:
                            raise ObjectNotModifiedException
                    else:
                        raise ObjectNotModifiedException

                except ObjectActionException as exception:
                    Log.debug('Could not modify requested object: {}'.format(obj))
                    raise

        return frontend_response

    def _update_server(self, frontend_response, em, mo, bAdd):
        """
        Helper method to send object CRUD request to the remote server
        """
        # Force server to choose ID, and append the owner ID ourselves.
        if bAdd:
            em.setFieldAsString("ID", "-1")
            em.setFieldAsString("OI", str(current_user.user_group_id))

        # Send the modify to rkserver
        backend_response = self.send(em.getText())

        # Get the response and deserialize it back into the managed object
        emResp = ExcryptMessage(backend_response)

        # Error occured in the job add
        if emResp.hasField("BB") and not emResp.hasField("ID"):
            frontend_response['result'] = 'Failure'
            frontend_response['message'] = emResp.getField("BB")
        else:
            mo.fromMessage(emResp)
            # Reserialize the object into json for the response
            self._update_response(mo, frontend_response)

    def _validate(self, server_request):
        """
        Validates object input's before sending CRUD operation to the server
        """
        frontend_response = {}

        validate_types = self._validate_whitelist()

        for k,v in server_request.data.items():
            for obj in v:
                try:
                    # Create managed object
                    em = None
                    object_id = v[0]["objectID"]
                    mo_name = k
                    mo_type = ManagedObjectUtils.getType(mo_name)

                    if mo_type not in validate_types:
                        raise ObjectNotValidatedException(manager=mo_type, reason="object type is not allowed")

                    # Deserialize into filter
                    if len(object_id) > 0:
                        filt = Filter()
                        filt.setManager(mo_name)
                        filt.setIDs(mo_type, object_id)

                        # Query server
                        backend_response = self.query_rk_filter(filt, current_user.context)

                        # If it exists, then fill out the existing object
                        if len(backend_response) > 1:
                            m = backend_response[0]
                            em = ExcryptMessage(m)

                    # Create the object
                    mo = ManagedObjectUtils.createObjectFromTypeTake(mo_type, 0)

                    if mo is not None:
                        # If the object exists, use the existing object as a template.
                        # Otherwise, create a new object
                        if em:
                            mo.fromMessage(em)
                        else:
                            em = ExcryptMessage()

                        # Deserialize into managed object
                        mo.fromJSONString(json.dumps(obj), librk.eMOActionCreate)

                        # Serialize into Excrypt message
                        mo.toMessage(em)
                        em.setFieldAsString("AO", "RKY107")
                        em.setFieldAsString("MN", k)

                        # Send the modify to rkserver
                        try:
                            backend_response = self.send(em.getText())
                        except MissingConnectionException:
                            raise

                        # Handle backend_response
                        emResp = ExcryptMessage(backend_response)
                        result = True if emResp.getField("AN") == "Y" else False
                        message = emResp.getField("BB")
                    else:
                        raise ObjectNotValidatedException
                except:
                    raise ObjectNotValidatedException

        frontend_response = { "result": result, "message": message }
        return frontend_response

    def _formdata(self, server_request, request_types, name):
        """
        Get form data for an object
        """
        frontend_response = None
        request_values = server_request.data.get(name)
        request_type = request_types.get(name)
        if request_values and request_type:
            frontend_response = self._get_formdata(request_type, request_values)
        else:
            Log.error('Received invalid form-data type (%s) and name (%s)' % (request_type, name))

        return frontend_response

    def _get_mos(self, manager, backend_response):
        """
        Helper method to aggregate frontend mo response from backend response
        """
        frontend_response = {manager: []}

        # We always want backend_response to be a list of responses
        if isinstance(backend_response, (str, bytes)):
            backend_response = [backend_response]

        for m in backend_response:
            em = ExcryptMessage(m)
            mo = ManagedObjectUtils.createObjectFromTypeTake(ManagedObject.TYPE(em.getFieldAsInt("TY")), 0)
            if mo is not None:
                mo.fromMessage(em)

                # Update the object for external consumption
                self._sanitize_object(mo)

                mo_name = ManagedObjectUtils.getManagerName(mo.getType())
                frontend_response.setdefault(mo_name, []).append(mo.toJSONString())

        return frontend_response

    def _get_mo_count(self, manager, backend_response):
        """
        Helper method to get managed object count from backend response
        """
        frontend_response = {manager: []}

        # Get the count from the backend response
        em = ExcryptMessage(backend_response)
        mo_count = em.getFieldAsInt("MC")

        # Add the count to the frontend response
        frontend_response[manager].append(json.dumps({'count': mo_count}))

        return frontend_response

    def _check_clauses(self, query):
        """Check a filter's clauses
        Parameters:
            query: the filter query object
        Returns: true on success false otherwise
        """
        # TODO - This should fail by default and get overridden by the app code
        return ''

    def _delete(self, server_request):
        """Delete IDs from the message
        Arguments:
            server_request: the received delete request
        Returns: A JSON response with result of Failure or Success
        """
        delete_types = self._delete_whitelist()

        # Don't process delete requests from the anonymous group
        if current_user.context.is_anonymous():
            return None

        frontend_response = {}
        mo_id = -1
        mo_type = ManagedObject.UNKNOWN

        try:
            for manager, ids in server_request.data.items():
                mo_type = ManagedObjectUtils.getType(manager)
                frontend_response[manager] = []

                if mo_type not in delete_types:
                    raise ObjectNotDeletedException(manager=manager, oid=ids, reason="object type is not allowed")

                filter_response = self.check_permission(manager, ids, librk.eMOActionDelete)
                deletable_ids = filter_response and (ExcryptMessage(filter_response[0]).getField('VB') or '').split(',')
                impermissible_ids = set(ids) - set(deletable_ids)
                if impermissible_ids:
                    raise ObjectNotDeletedException(manager=manager, oid=','.join(impermissible_ids))

                for mo_id in ids:
                    if self.delete_object(manager, mo_id):
                        frontend_response[manager].append(mo_id)

        except ObjectActionException as exception:
            Log.debug('Could not delete requested object: {}, {}'.format(mo_type, mo_id))
            raise

        return frontend_response

    def _add_whitelist(self):
        """ Gets allowed managed object types that can be added.
        Returns: A list of types that are allowed to be added.
        """
        return []

    def _modify_whitelist(self):
        """ Gets allowed managed object types that can be modified.
        Returns: A list of types that are allowed to be modified.
        """
        return self._add_whitelist()

    def _validate_whitelist(self):
        """ Gets allowed managed object types that can be modified.
        Returns: A list of types that are allowed to be modified.
        """
        return self._add_whitelist()

    def _delete_whitelist(self):
        """ Gets allowed managed object types that can be deleted
        Returns: A list of types that are allowed to be deleted
        """
        return []

    def _filter_whitelist(self):
        """ Gets allowed managed object types that can be filtered.
        Returns: A list of types that are allowed to be filtered.
        """
        return []

    def _all_filter_types_allowed(self, manager_list):
        """Checks to see that all managers specified in a filter are allowed.

        Arguments:
            manager_list {list} -- Manager list.

        Returns:
            bool -- True if all managers are acceptable, false otherwise.
        """

        for manager in manager_list:
            if manager not in self._filter_whitelist():
                Log.error("Managed object type " + str(manager) + " not allowed in filter.")
                return False

        return True

    def _is_routed_to_group(self, auth_credentials):
        """
        Are these credentials for a group?
        """
        return "GROUP" in auth_credentials.get("objectType")

    def _set_multi_balanced_device_info(self, object_info, message):
        """Helper method to add balancer tags to messages.
        Arguments:
            object_info: Dict with object id and object type
            message: ExcryptMessage to add tags to
        """
        object_id = object_info.get('objectID')
        object_parent_id = object_info.get('objectParentID')

        if self._is_routed_to_group(object_info):
            message.setFieldAsString('ZZ', object_id)
        else:
            message.setFieldAsString('ZY', object_id)
            message.setFieldAsString('ZZ', object_parent_id)

    def get_major_keys(self, server_request):
        """Gets the major key checksums for the given device.

        Arguments:
            device_info {object} -- Device to get checksums for.
        """

        checksums_message = self._get_checksum_message(server_request);

        frontend_response = {"result": "Failure",
                             "message": "Could not retrieve major key checksums."}

        try:
            rsp_msg = ExcryptMessage(self.send(checksums_message.getText()))

            checksums_tag = self._get_checksum_tag_value(server_request, rsp_msg)
            key_checksum_pairs = self._parse_major_key_checksums(
                checksums_tag)

            frontend_response = {"result": "Success",
                                 "checksums": key_checksum_pairs}

        except:
            Log.error("Error when retrieving major key checksums")

        return frontend_response

    def _get_checksum_message(self, server_request):
        """Returns the message we send to backend to get major key checksums

        Arguments:
            server_request - frontend json request

        Returns:
            An ExcryptMessage with the backend request
        """
        checksums_message =  ExcryptMessage("[AOSKEY;BJ9;]")
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
        return backend_response.getField('AE')

    def _parse_major_key_checksums(self, major_key_string):
        """Parses a major key checksum string into a dict of key to checksum.

        Arguments:
            major_key_string {string} -- Major key checksum string.
        """

        # String looks like "MFK:1234:PMK:3456: ... ..."
        key_checksum_pairs = {}
        checksums = major_key_string.split(":")

        it = iter(checksums)

        # Pair the major key name with its checksum.
        for checksum in it:
            key_checksum_pairs[checksum] = next(it)

        return key_checksum_pairs
