"""
@file      byok/views/clusters.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Views for cluster management
"""

from typing import Optional, cast

import byok.models.clusters as models
import byok.translators.clusters as translators
from byok import Blueprint, BaseResponse, ByokView, abort, translate_with
from byok.utils.key_table import invalidates_keytable_cache


bp = Blueprint(
    name='Cluster Management',
    description='Manage sessions with device groups',
)


@bp.route('/clusters')
class ClustersView(ByokView):
    @bp.success(models.DeviceGroupList)
    @translate_with(translators.GDLB_list)
    def get(self):
        """
        List clusters

        Retrieve a list of device groups
        """


@bp.route('/clusters/<groupId>')
class ClusterManagementView(ByokView):

    errors = {
        'INSUFFICIENT CLUSTER PERMISSIONS': 403,
        'FAILED TO FIND CLUSTER': 404,
        'COULD NOT FIND GROUP': 404,
    }

    @bp.success(models.DeviceGroup)
    @translate_with(translators.GDLB_get, postprocess=True)
    def get(self, response: models.DeviceGroup):
        """
        Retrieve cluster

        Get details about a device group
        """
        feature_list = self.get_feature_list(groupId=response.id)
        response.features = feature_list.features
        return response

    @translate_with(translators.GDGD_read_features, preprocess=True, postprocess=True)
    def get_feature_list(self, groupId: Optional[str] = None, response=None) -> models.FeaturesDump:
        """
        Connect and retrieve cluster features
        """
        if response:  # postprocessing, just clean up our connection
            end_session = translate_with(translators.GDGD_disconnect)(lambda: ...)
            end_session(self, sessionId=self.session_id)
            return response

        # preprocessing, make a sessionId to connect to
        assert groupId
        make_session = translate_with(translators.GDGD_connect)(lambda: ...)
        session = make_session(self, models.Session(group=groupId))
        self.session_id = cast(models.Session, session).id
        return (self.session_id, )  # type: ignore (args tuple to GDKM_read_features.serialize)


@bp.route('/clusters/sessions')
class SessionsView(ByokView):

    errors = {
        'INSUFFICIENT CLUSTER PERMISSIONS': 403,
        'FAILED TO FIND CLUSTER': 404,
    }

    @bp.success(models.SessionList)
    @translate_with(translators.GDGD_list_sessions)
    def get(self):
        """
        List sessions

        Get a list of open device group sessions
        """

    @bp.json(models.Session, example={'group': '{01641505-7B5A-0002-0011-FB141CED9B38}'})
    @bp.success(models.Session)
    @translate_with(translators.GDGD_connect)
    def post(self):
        """
        Connect to cluster

        Creates a session with a device group
        """


@bp.route('/clusters/sessions/<sessionId>')
class SessionManagementView(ByokView):

    errors = {
        'SESSION NOT FOUND': 404,
    }

    @bp.success(BaseResponse)
    @translate_with(translators.GDGD_disconnect)
    def delete(self):
        """
        Disconnect from cluster

        Closes a device group session
        """


@bp.route('/clusters/sessions/<sessionId>/login')
class SessionLoginView(ByokView):

    errors = {
        'SESSION NOT FOUND': 404,
    }

    @bp.json(models.ClusterLoginIntent)
    @bp.success(models.ClusterAuthorizationState)
    def post(self, req: models.ClusterLoginIntent, sessionId: str):
        """
        Cluster login

        Authenticate to device group
        """
        TYPES = {
            'userpass': translators.GDGD_login_pw,
            'u2f': translators.GDGD_login_u2f,
        }
        translator = TYPES[req.authType]
        translator = translate_with(translator)(lambda: ...)
        return translator(self, req.authCredentials, sessionId=sessionId)

    @bp.success(models.ClusterAuthorizationState)
    @translate_with(translators.GDGD_login_status)
    def get(self):
        """
        Cluster login status

        Retrieve session authorization state
        """

    def handle_errors(self, msg):
        status = msg.get('CN')
        if status == 'Y' or status == 'C':
            return

        err_msg = msg.get('ER') or msg.get('BB')
        status_code = self.errors.get(err_msg, 500)
        abort(status_code, err_msg)


@bp.route('/clusters/sessions/<sessionId>/logout')
class SessionLogoutView(ByokView):

    errors = {
        'SESSION NOT FOUND': 404,
    }

    @invalidates_keytable_cache
    @bp.success(BaseResponse)
    @translate_with(translators.GDGD_logout)
    def post(self):
        """
        Cluster logout

        Ends session with device group
        """

    def handle_errors(self, msg):
        # status could be CN (from firmware)
        status = msg.get('CN')
        if status == 'Y':
            return

        err_msg = msg.get('ER') or msg.get('BB')
        status_code = self.errors.get(err_msg, 500)
        abort(status_code, err_msg)


@bp.route('/clusters/sessions/<sessionId>/settings', document=False)
class SessionSettingsView(ByokView):

    errors = {
        'SESSION NOT FOUND': 404,
    }

    @bp.success(models.SettingsDump)
    @translate_with(translators.GDGD_get_settings)
    def get(self):
        """
        Retrieve cluster settings
        """

    def handle_errors(self, msg):
        if msg.get('BB'):
            super().handle_errors(msg)
