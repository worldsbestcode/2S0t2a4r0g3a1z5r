"""
@file      kmes/views/token_profiles.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES token group profile view
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route


@Route()
class TokenProfile(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "TokenProfiles")

    def post(self):
        request_data = request.get_json()

        response = self.translate("Create", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "TG":
            return APIResponses.conflict(message=message)
        elif "PERMISSION" in message or status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.failure(message=message)

    @Route.get("*")
    def retrieve_list(self):
        request_data = request.args.to_dict(flat=True)
        response = self.translate("List", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif message == "INVALID CHUNK":
            return APIResponses.not_found(message="Page out of range")
        else:
            return APIResponses.bad_request(message=message)

    @Route.get("id")
    def retrieve_single(self):
        request_data = request.args.to_dict(flat=True)
        response = self.translate("Retrieve", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif "INVALID TOKEN" in message or "MASKED LENGTH" in message:
            return APIResponses.bad_request(message=message)
        elif "PERMISSIONS" in message or status == "P":
            return APIResponses.forbidden(message)
        elif "NONEXISTENT" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.not_found(message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("Update", request_data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif "INSUFFICIENT PERMISSION" in message or status == "P":
            return APIResponses.forbidden(message)
        elif "NONEXISTENT" in message:
            return APIResponses.not_found(message)
        elif "INVALID" in message:
            return APIResponses.bad_request(message=message)
        elif "FAILED TO MODIFY" in message:
            return APIResponses.failure(message)
        else:
            return APIResponses.failure(message)

    def delete(self):
        response = self.translate("Delete", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success()
        elif "NONEXISTENT" in message:
            return APIResponses.not_found(message=message)
        elif "PERMISSIONS" in message or status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.failure(message=message)


class Permissions(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "TokenProfiles")

    def get(self):
        response = self.translate("RetrievePermissions", request.args)
        status, message = response.pop("status", "N"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("UpdatePermissions", request_data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)


class Tokenize(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "TokenProfiles")

    def post(self):
        request_data = request.get_json()
        response = self.translate("Tokenize", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)


class Detokenize(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "TokenProfiles")

    def post(self):
        request_data = request.get_json()
        request_data["verifyOnly"] = False
        response = self.translate("Detokenize", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)


class VerifyToken(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "TokenProfiles")

    def post(self):
        request_data = request.get_json()
        request_data["verifyOnly"] = True
        response = self.translate("Detokenize", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)
