"""
@file      byok/views/users.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Views for roles and identities management
"""

from typing import TYPE_CHECKING, cast

import gevent
from flask_login import current_user

import byok.models.users as models
import byok.translators.users as translators
from byok import BaseResponse, Blueprint, ByokView, abort, translate_with
from byok.models.base import BasePaginationIntent
from byok.models.clusters import ClusterAuthorizationState
from byok.translators.clusters import GDGD_login_status

if TYPE_CHECKING:
    from lib.auth.user import User
    current_user = cast(User, current_user)


bp = Blueprint(
    name='Roles and Identities',
    description='Manage user roles and identities on a remote device group',
)


@bp.route('/clusters/sessions/<sessionId>/roles')
class RolesView(ByokView):

    errors = {
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
    }

    @bp.params(BasePaginationIntent)
    @bp.success(models.RoleList)
    @translate_with(translators.GDGD_list_roles, preprocess=True, postprocess=True)
    def get(self,
            data: BasePaginationIntent = None,
            sessionId: str = None,
            response: models.RoleList = None):
        """
        List roles

        Get a list of user roles available in a device group
        """
        if data:  # preprocess
            self.page = data.page
            self.page_count = data.pageCount
            return data, sessionId
        if response:  # postprocess
            response.page = self.page
            response.pageCount = self.page_count
            response.update_pagination()
            return response


@bp.route('/clusters/sessions/<sessionId>/identities')
class IdentitiesView(ByokView):

    errors = {
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
        'VALUE OUT OF RANGE': 404,
        'LABEL NOT UNIQUE': 409,
    }

    ignore_perm_error = False

    def handle_errors(self, msg):
        # for GET, don't abort for a perms error as we will use then GUSR instead
        if (msg.message == 'INSUFFICIENT PERMISSION' and self.ignore_perm_error):
            return
        super().handle_errors(msg)

    @bp.params(models.IdentityListIntent)
    @bp.success(models.IdentityList)
    @translate_with(translators.GDGD_list_identities, preprocess=True, postprocess=True)
    def get(self, data: models.IdentityListIntent = None, sessionId: str = None, response=None):
        """
        List identities

        Get a list of user identities available in a device group
        """
        self.ignore_perm_error = True

        if data:  # preprocess
            self.page = data.page
            self.page_count = data.pageCount
            self.session_id = sessionId
            return data, sessionId

        if response:  # postprocess
            # if they don't have Identity perms, return their logged in identities as unmanageable
            if not response.identities:
                response = self.get_unmanaged_identities()
            # otherwise their identities would already be in the response
            else:
                self.add_identity_details(response)

            response.page = self.page
            response.pageCount = self.page_count
            response.update_pagination()

            return response


    @bp.json(models.Identity)
    @bp.success(BaseResponse)
    @translate_with(translators.GDGD_create_identity)
    def post(self):
        """
        Create identity

        Add a user identity to a device group
        """

    def get_unmanaged_identities(self) -> models.IdentityList:
        """Make an IdentityList from the logged in identities"""

        results: 'list[models.IdentitySummary]' = []

        # Get authenticated identities from AOGUSR;LO0
        get_session_info = translate_with(GDGD_login_status, handle_errors=False)(lambda: None)
        status = cast(ClusterAuthorizationState, get_session_info(self, sessionId=self.session_id))
        index_start = (self.page - 1) * self.page_count
        index_end = self.page * self.page_count + 1
        identity_names = status.identities[index_start:index_end]

        # Get the u2f token status for those users
        get_u2f = translate_with(translators.GDGD_read_u2f, handle_errors=False)(lambda: None)
        for name in identity_names:
            id_credentials = cast(models.U2fCredentialList,
                                  get_u2f(self, sessionId=self.session_id, identity=name))
            results.append(models.IdentitySummary(
                name=name,
                locked=False,  # logged in.. can't be locked
                type='Administration',  # logged into admin port, must be admin type
                manageable=False,  # didn't show up in the IDEN list -> not manageable
                u2fEnabled=bool(id_credentials.u2fCredentials),
            ))

        return models.IdentityList(identities=results)

    def add_identity_details(self, response: models.IdentityList):
        """Retrieve the details of each identity and update the IdentityList"""
        @translate_with(translators.GDGD_read_identity, context=current_user.context)
        def read_identity():
            pass

        threads = [
            gevent.spawn(read_identity, self, self.session_id, identity.name)
            for identity in response.identities if identity.manageable
        ]
        gevent.joinall(threads)
        for response_identity, thread in zip(response.identities, threads):
            if thread.value:
                response_identity.locked = thread.value.locked
                response_identity.u2fEnabled = bool(thread.value.u2fCredentials)


@bp.route('/clusters/sessions/<sessionId>/identities/<identity>')
class IdentityView(ByokView):

    errors = {
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
        'VALUE OUT OF RANGE': 404,
        'LABEL NOT UNIQUE': 409,
    }

    @bp.success(models.Identity)
    @translate_with(translators.GDGD_read_identity)
    def get(self):
        """
        Retrieve identity

        Get details about a user identity from a device group
        """

    @bp.json(models.Identity)
    @bp.success(BaseResponse)
    @translate_with(translators.GDGD_update_identity)
    def put(self):
        """
        Update identity

        Modify a user identity in a device group
        """

    @bp.success(BaseResponse)
    @translate_with(translators.GDGD_delete_identity)
    def delete(self):
        """
        Delete identity

        Delete a user identity in a device group
        """


@bp.route('/clusters/sessions/<sessionId>/identities/<identity>/change-password')
class ChangePasswordView(ByokView):

    errors = {
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
        'VALUE OUT OF RANGE': 404,
        'LABEL NOT UNIQUE': 409,
        'Default password specified.': 422,
        'Password .*': 422,
        'Not enough .*': 422,
    }

    def handle_errors(self, msg):
        if (msg.get('AN') == 'PW' and msg.get('BB') == 'VALUE OUT OF RANGE'):
            abort(400, 'Incorrect password')
        return super().handle_errors(msg)

    @bp.json(models.ChangePasswordIntent)
    @bp.success(BaseResponse)
    @translate_with(translators.GDGD_change_password)
    def post(self):
        """
        Change Password

        Set an identity's password in a device group
        """


@bp.route('/clusters/sessions/<sessionId>/identities/<identity>/u2f/<name>')
class U2fView(ByokView):

    errors = {
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
        'VALUE OUT OF RANGE': 404,
        'LABEL NOT UNIQUE': 409,
    }

    def handle_errors(self, msg):
        # CN tag != Y with no BB tag (match empty str) is still success
        if msg.get('CN', 'N') != 'N':
            return
        return super().handle_errors(msg)

    @bp.json(models.U2fRegisterIntent, required=False)
    @bp.success(models.U2fRegisterResponse)
    @translate_with(translators.GDGD_register_u2f)
    def post(self):
        """
        Register U2F credential
        """

    @bp.success(BaseResponse)
    @translate_with(translators.GDGD_delete_u2f)
    def delete(self):
        """
        Delete U2F credential
        """
