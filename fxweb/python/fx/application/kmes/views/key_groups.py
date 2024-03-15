"""
@file      kmes/views/key_groups.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES key group view
"""
from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses


class KeyGroups(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "KeyGroups")

    def get(self):
        data = request.args
        response = self.translate("List", data)

        status, message = response.pop("status", "Y"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)


class MoveKeyGroup(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "KeyGroups")

    def put(self):
        data = request.get_json()
        response = self.translate("Move", data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success(message=message)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif message.lower() in ("unknown group", "unknown key group"):
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)


class KeyGroupsPermissions(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "KeyGroups")

    def get(self):

        data = request.args
        response = self.translate("RetrievePermissions", data)

        status, message = response.pop("status", "Y"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
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
        else:
            return APIResponses.failure(message=message)


class KeyFolders(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "KeyFolders")

    def post(self):
        data = request.get_json()
        response = self.translate("Create", data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message=message, body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif status == "A":
            return APIResponses.conflict(message=message)
        else:
            return APIResponses.failure(message=message)

    def get(self):
        data = request.args
        response = self.translate("Retrieve", data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if response.pop("type", "") == "store":
            return APIResponses.not_found()
        elif status == "Y":
            return APIResponses.success(message=message, body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.not_found(message=message)

    def put(self):
        data = request.get_json()
        response = self.translate("Update", data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success(message=message)
        elif status == "A":  # name in use
            return APIResponses.conflict(message=message)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif message.lower() in ("unknown group", "unknown key group"):
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)

    def delete(self):
        data = request.args
        response = self.translate("Delete", data)

        status, message = response.get("status"), response.get("message", "")
        if status == "Y":
            return APIResponses.success(message=message)
        elif status == "P" or "permissions" in message.lower():
            return APIResponses.forbidden(message=message)
        elif message.lower() in ("unknown key group", "key group not found"):
            return APIResponses.not_found()
        else:
            return APIResponses.failure(message=message)


class KeyStores(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "KeyStores")

    def get(self):
        data = request.args
        response = self.translate("Retrieve", data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if response.pop("type", "") == "folder":
            return APIResponses.not_found()
        elif status == "Y":
            return APIResponses.success(message=message, body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.not_found(message=message)

    def put(self):
        data = request.get_json()
        response = self.translate("Update", data)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success(message=message)
        elif status == "A":  # name in use
            return APIResponses.conflict(message=message)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif message.lower() in ("unknown group", "unknown key group"):
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)

    def delete(self):
        data = request.args
        response = self.translate("Delete", data)

        status, message = response.get("status"), response.get("message", "")
        if status == "Y":
            return APIResponses.success(message=message)
        elif status == "P" or "permissions" in message.lower():

            return APIResponses.forbidden(message=message)
        elif message.lower() in ("unknown key group", "key group not found"):
            return APIResponses.not_found()
        else:
            return APIResponses.failure(message=message)


class RotateKeyStore(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "KeyStores")

    def post(self):
        data = request.get_json()
        response = self.translate("Rotate", data)

        status, message = response.pop("status"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P" or "PERMISSIONS" in message:
            return APIResponses.forbidden(message=message)
        elif message == "UNKNOWN KEY GROUP":
            return APIResponses.not_found(message=message)
        elif "No key template" in message or "regenerative KRA" in message:
            return APIResponses.conflict(message=message)
        else:
            return APIResponses.failure(message=message)
