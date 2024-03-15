"""
@file      kmes/views/issuance_policies.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the Issuance Policies views
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route


@Route()
class IssuancePolicy(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "IssuancePolicies")

    def post(self):
        request_data = request.get_json()

        response = self.translate("Create", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif status == "A":
            return APIResponses.conflict(message=message)
        else:
            return APIResponses.failure(message=message)

    @Route.get("*")
    def get_list(self):
        response = self.translate("List", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.not_found(message=message)

    @Route.get({"id", "signingCertId", "signingCert"})
    def get_single(self):
        response = self.translate("Retrieve", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y" and not response.get("id"):
            # RAGA returns defaults if the certificate has no issuance policy
            return APIResponses.not_found(message="ISSUANCE POLICY NOT FOUND")
        elif status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.not_found(message=message)

    def put(self):
        request_data = request.get_json()

        response = self.translate("Update", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.failure(message=message)

    def delete(self):
        response = self.translate("Delete", request.args)

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "UNKNOWN" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)
