"""
@file      kmes/views/users.py
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
class Users(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Users")

    def post(self):
        request_data = request.get_json()

        response = self.translate("Create", request_data)

        status, message = response.get("status", "Y"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        elif status == "A":  # We don't get a message for status 'A'
            return APIResponses.failure("Username already exists")
        else:
            return APIResponses.failure(message)

    @Route.get(["usergroup", "*"])
    def get_list(self):
        response = self.translate("List", request.args.to_dict(flat=True))

        status, message = response.pop("status", "Y"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif status == "N":
            return APIResponses.not_found(message)
        else:  # status is Excrypt tag that was malformed
            return APIResponses.bad_request(message)

    @Route.get("username")
    def get_single(self):
        response = self.translate("Retrieve", request.args.to_dict(flat=True))

        status, message = response.pop("status", "Y"), response.pop("message", "")
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
            return APIResponses.success(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    def delete(self):
        response = self.translate("Delete", request.args)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        elif status == "N" and "unknown" in message.lower():
            return APIResponses.not_found(message)
        else:  # name conflict, deletion would leave <2 admins on card, etc.
            return APIResponses.failure(message)


class MoveUser(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Users")

    def put(self):
        request_data = request.get_json()
        response = self.translate("Move", request_data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)


class ChangeUserPassword(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Users")

    def post(self):
        request_data = request.get_json()

        response = self.translate("SetPassword", request_data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)
