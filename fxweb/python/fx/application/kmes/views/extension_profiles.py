"""
@file      kmes/views/extension_profiles.py
@author    Dalton McGee(dmcgee@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES X.509 V3 Extension Profiles View
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route


@Route()
class X509ExtensionProfiles(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ExtensionProfiles")

    def post(self):
        request_data = request.get_json()
        response = self.translate("Create", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "A":
            return APIResponses.conflict(message)
        elif "PERMISSION" in message or status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.failure(message=message)

    @Route.get("*")
    def get_list(self):
        request_data = request.args
        response = self.translate("List", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif "INVALID NAME" in message:
            return APIResponses.bad_request(message=message)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)

    @Route.get(("id", "name"))
    def get(self):
        request_data = request.args
        response = self.translate("Retrieve", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif "INVALID NAME" in message or "UNKNOWN" in message:
            return APIResponses.bad_request(message=message)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)

    def put(self):
        data = request.get_json()
        response = self.translate("Update", data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success(message=message)
        elif "INVALID NAME" in message or "NOT FOUND" in message:
            return APIResponses.bad_request(message=message)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.failure(message=message)

    def delete(self):
        request_data = request.args
        response = self.translate("Delete", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.not_found(message)
        elif "NOT FOUND" in message or "UNKNOWN" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.failure(message)


class X509ExtensionPermissions(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ExtensionProfiles")

    def get(self):
        request_data = request.args
        response = self.translate("RetrievePermissions", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "FAILED" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.bad_request(message=message)

    def put(self):
        data = request.get_json()
        response = self.translate("UpdatePermissions", data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success(message=message)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "FAILED" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)
