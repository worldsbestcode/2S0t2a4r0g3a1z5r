"""
@file      kmes/views/object_signing.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for Object Signing Requests
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route


@Route()
class ObjectSigningRequests(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ApprovalRequests")

    def post(self):
        request_data = request.get_json()
        response = self.translate("CreateObjSigningRequest", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        message = message.replace("GN TAG NOT GIVEN ", "APPROVAL GROUP NOT SPECIFIED ")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif "NOT FOUND" in message or "UNKNOWN" in message:
            return APIResponses.not_found(message)
        elif "LDAP CREDENTIALS REQUIRED" in message or "LDAP AUTHENTICATION FAILURE" in message:
            return APIResponses.unauthorized(message)
        else:
            return APIResponses.failure(message)

    @Route.get("*")
    def get_list(self):
        request_data = request.args.to_dict(flat=True)

        response = self.translate("ListObjSigningRequests", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)

    @Route.get("requestId")
    def get(self):
        request_data = request.args.to_dict(flat=True)

        response = self.translate("RetrieveObjSigningRequest", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "UNKNOWN" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.bad_request(message=message)

    def put(self):
        request_data = request.get_json()

        response = self.translate("UpdateObjSigningRequest", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif "NOT FOUND" in message or "UNKNOWN" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.failure(message)
