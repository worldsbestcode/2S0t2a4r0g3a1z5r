"""
@file      kmes/views/approval_groups.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the Signing Approval Groups view
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route


@Route()
class ApprovalGroups(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ApprovalGroups")

    def post(self):
        request_data = request.get_json()
        response = self.translate("Create", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif message == "NAME ALREADY EXISTS":
            return APIResponses.conflict(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)

    @Route.get("*")
    def get_list(self):
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

    @Route.get({"id": "*", "name": "*"})
    def get_single(self):
        response = self.translate("Retrieve", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    def put(self):
        request_data = request.get_json()

        response = self.translate("Update", request_data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif message == "NAME ALREADY EXISTS":
            return APIResponses.conflict(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)

    def delete(self):
        response = self.translate("Delete", request.args)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif message == "INVALID APPROVAL GROUP":
            return APIResponses.not_found(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)


class Permissions(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ApprovalGroups")

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
