"""
@file      guardian_views.py
@author    Tim Brabant(tbrabant@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Implements the URIs that serve the files for the Guardian views.
"""

import urllib.parse
from flask_login import current_user
from flask import request, jsonify
from server_request import ServerRequest
from app_sanitize import sanitize_request
from app_csrf import csrf_required
from rk_formdata import RKFormDataView

from base import server_views
from base import server_files
from guardian import guardian_files
from rk_application import views as rk_application_views


def map_views(program):
    endpoints = {
        '/'                                                 : server_views.ServerDefaultView,
        '/object'                                           : server_views.ServerObjectView,
        '/logininfo'                                        : server_views.ServerLoginInfoView,
        '/systemInfo'                                       : rk_application_views.SystemInfoView,
        '/formdata'                                         : GuardianFormDataView,
        '/download/<filename>'                              : guardian_files.GuardianDownloadView,
    }

    files = {
        '/<filename>'                                   : server_files.ServerAppFiles,
        '/directives/<filename>'                        : server_files.ServerAppDirectivesFiles,
        '/components/<filename>'                        : server_files.ServerAppComponentsFiles,
        '/components/idioms/<filename>'                 : server_files.ServerAppComponentsIdiomsFiles,
        '/components/sections/<filename>'               : server_files.ServerAppComponentsSectionsFiles,
        '/components/sections/nodeView/<filename>'      : guardian_files.GuardianAppComponentsSectionsNodeviewFiles,
        '/components/sections/config/<filename>'        : guardian_files.GuardianAppComponentsSectionsConfigFiles,
        '/components/sections/peer/<filename>'          : guardian_files.GuardianAppComponentsSectionsPeerFiles,
    }

    # Prefix API with project name and API version
    final_views = {}
    for prefix, view in endpoints.items():
        final_views['/guardian/v1' + prefix] = view

    for prefix, view in files.items():
        final_views['/guardian' + prefix] = view

    return final_views

class GuardianFormDataView(RKFormDataView):
    """
    Form Data View that handles getting form data and communicating with remote devices.
    """
    decorators = [sanitize_request, csrf_required]

    _REQUEST_TYPES = {
        'remote_login': {
            "name": "remote_login",
            'fields': ['login_data']
        },
        'remote_logout': {
            "name": "remote_logout",
            'fields': ['logout_data']
        }
    }

    def post(self, *args, **kwargs):
        """
        Retrieve form data.
        """
        post_data = request.get_json()
        frontend_response = {}

        method = post_data['method']
        if method == 'retrieve':
            return super(GuardianFormDataView, self).post(*args, **kwargs)
        elif method == 'remote_control':
            frontend_response = self.server_interface.formdata(
                ServerRequest(request, post_data["formData"]),
                self._REQUEST_TYPES,
                post_data.get('name')
            )

        result = "Failure"

        if frontend_response and frontend_response.get("result") != "Failure":
            result = "Success"

        ret_msg = jsonify(result=result, formData=frontend_response)
        ret_msg.set_cookie("authed_ids",
                           urllib.parse.quote(current_user.get_authed_ids_cookie()))

        return ret_msg
