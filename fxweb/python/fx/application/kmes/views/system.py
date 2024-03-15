"""
@file      kmes/views/system.py
@author    Jamal Al(jal@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES system view
"""
from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses


class AutoBackup(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "System")

    def get(self):
        response = self.translate("RetrieveAutoBackup", request.args.to_dict(flat=True))
        status, message = response.pop("status", "N"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("UpdateAutoBackup", request_data)
        status, message = response.get("status", "N"), response.get("message", "")

        if status == "Y":
            return APIResponses.success(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif status == "N":
            return APIResponses.bad_request(message)
        else:
            return APIResponses.failure(message)


class Certificates(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "System")

    def get(self):
        response = self.translate("RetrieveCertificates", request.args.to_dict(flat=True))

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("UpdateCertificates", request_data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)


class GlobalPermissions(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "System")

    def get(self):
        response = self.translate("RetrieveGlobalPermissions", request.args.to_dict(flat=True))
        status, message = response.pop("status", "N"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("UpdateGlobalPermissions", request_data)
        status, message = response.get("status", "N"), response.get("message", "")

        if status == "Y":
            return APIResponses.success(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif status == "N" or status == "PS" or "MISMATCH" in message:
            return APIResponses.bad_request(message)
        else:
            return APIResponses.failure(message)


class Ntp(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "System")

    def get(self):
        response = self.translate("RetrieveNtp", request.args.to_dict(flat=True))

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("UpdateNtp", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)


class RaSettings(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "System")

    def get(self):
        request_data = request.args.to_dict(flat=True)
        response = self.translate("RetrieveRaSettings", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    def put(self):
        request_data = request.get_json()

        # Convert approvalType (if exists) string to upper case
        # to avoid errors due to capitalization
        approvalType = request_data.pop("approvalType", False)
        if approvalType:
            request_data["approvalType"] = approvalType.upper()

        response = self.translate("UpdateRaSettings", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif status == "N":
            return APIResponses.bad_request(message)
        else:
            return APIResponses.not_found(message)


class SecureMode(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "System")

    def get(self):
        request_data = request.args.to_dict(flat=True)
        response = self.translate("RetrieveSecureMode", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    def put(self):
        request_data = request.get_json()

        response = self.translate("UpdateSecureMode", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif status == "N":
            return APIResponses.bad_request(message)
        else:
            return APIResponses.not_found(message)
