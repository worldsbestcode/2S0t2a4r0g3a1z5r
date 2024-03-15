"""
@file      kmes/views/user_groups.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES user group view
"""
from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route


@Route()
class UserGroups(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "UserGroups")

    def post(self):
        request_data = request.get_json()
        response = self.translate("Create", request_data)

        status, message = response.get("status", "Y"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)

    @Route.get(["*", "parent"])
    def get_list(self):
        response = self.translate("List", request.args.to_dict(flat=True))

        status, message = response.pop("status"), response.pop("message")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    @Route.get("group")
    def get_single(self):
        response = self.translate("Retrieve", request.args.to_dict(flat=True))

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":  # Insufficient permissions
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("Update", request_data)

        status, message = response.get("status", "Y"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)

    def delete(self, *args, **kwargs):
        if not request.args.get("group", ""):
            return APIResponses.missing_argument("group")

        response = self.translate("Delete", request.args)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        elif status == "N" and "unknown" in message.lower():
            return APIResponses.not_found(message)
        else:
            return APIResponses.failure(message)


class MoveUserGroup(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "UserGroups")

    def put(self):
        request_data = request.get_json()
        response = self.translate("Move", request_data)

        status, message = response.get("status", "Y"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)
