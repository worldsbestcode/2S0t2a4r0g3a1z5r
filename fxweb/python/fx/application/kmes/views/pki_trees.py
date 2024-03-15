"""
@file      kmes/views/pki_trees.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES PKI Trees view
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route


@Route()
class PkiTree(ServerTranslatedView):
    """
    View class for managing PKI Trees
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "PKITrees")

    def post(self):
        request_data = request.get_json()
        response = self.translate("Create", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y" and not message:
            return APIResponses.success(message, response)
        elif status == "N":
            return APIResponses.failure(message=message)
        elif status == "A":
            return APIResponses.conflict()
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message=message)

    @Route.get("*")
    def list(self):
        response = self.translate("List", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "Success")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "N":
            return APIResponses.not_found(message=message)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message=message)

    @Route.get({"name", "id"})
    def get(self):
        response = self.translate("Retrieve", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y" and not message:
            return APIResponses.success(message, response)
        elif status == "N":
            return APIResponses.not_found(message=message)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message=message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("Update", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y" and not message:
            return APIResponses.success(message, response)
        elif status == "N":
            return APIResponses.failure(message=message)
        elif status == "A" or "already taken" in message:
            return APIResponses.conflict()
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message=message)

    def delete(self):
        response = self.translate("Delete", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif status == "N" and "invalid certificate" in message.lower():
            return APIResponses.not_found(message)
        else:
            return APIResponses.failure(message=message)


class PkiTreePermissions(ServerTranslatedView):
    """
    View class for managing the permissions of PKI Trees
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "PKITrees")

    def get(self):
        response = self.translate("RetrievePermissions", request.args.to_dict(flat=True))

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P" or "PERMISSIBLE GROUPS" in message:
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.not_found(message=message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("UpdatePermissions", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P" or "PERMISSIBLE GROUPS" in message:
            return APIResponses.forbidden(message=message)
        elif "FAILED TO LOOKUP" in message:
            return APIResponses.not_found(message=message)
        elif message == "GROUP CAN NOT HAVE THAT PERMISSION":
            return APIResponses.conflict()
        else:
            return APIResponses.failure(message=message)
