"""
@file      kmes/views/pki_generation.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for PKI Generation Requests
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route
from rk_host_application.rk_host_exceptions import FailedRAVD


@Route()
class PkiGenerationRequests(ServerTranslatedView):
    """
    View class for Approval requests generation
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ApprovalRequests")

    def post(self, *args, **kwargs):
        """
        Create a PKI approval request
        """
        request_data = request.get_json()

        try:
            response = self.translate("CreatePkiGenerationRequest", request_data)
        except FailedRAVD as e:
            if e.status == "P" or e.message == "NO PERMISSION":
                return APIResponses.forbidden("Insufficient permissions to apply DN Profile")
            return APIResponses.not_found(e.message)

        status, message = response.pop("status", "N"), response.pop("message", "")
        message = message.replace("GN TAG NOT GIVEN ", "APPROVAL GROUP NOT SPECIFIED ")
        message = message.replace("EN TAG NOT GIVEN ", "EXTENSION PROFILE NOT SPECIFIED ")
        if status == "Y" and not message:
            return APIResponses.success(body=response)
        elif status == "P" or message == "NO PERMISSION":
            return APIResponses.forbidden(message)
        elif "DUPLICATE CERTIFICATE COMMON NAME" in message:
            return APIResponses.conflict(message)
        elif "NOT FOUND" in message:
            return APIResponses.not_found(message)
        elif "LDAP " in message:
            return APIResponses.forbidden(message)
        elif "PKI GENERATION NOT ALLOWED" in message:
            return APIResponses.bad_request(message)
        else:
            return APIResponses.failure(message)

    @Route.get("requestId")
    def retrieve_pki(self, *args, **kwargs):
        """
        Retrieve a single PKI approval request
        """

        response = self.translate("RetrievePkiGenerationRequest", request.args)
        status, message = response.pop("status", "N"), response.pop("message", "")

        if status == "Y" and not message:
            return APIResponses.success(body=response)
        elif "PERMISSION" in message or status == "P":
            return APIResponses.forbidden(message)
        elif "UNKNOWN " in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.internal_error(message)

    @Route.get("*")
    def get(self):
        """
        List PKI approval request
        """

        request_data = request.args.to_dict(flat=True)
        response = self.translate("ListPkiGenerationRequests", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)

    def put(self):
        request_data = request.get_json()

        response = self.translate("UpdatePkiGenerationRequest", request_data)
        status, message = response.get("status", "N"), response.get("message", "")
        message = message.replace("GN TAG NOT GIVEN ", "APPROVAL GROUP NOT SPECIFIED ")
        message = message.replace("EN TAG NOT GIVEN ", "EXTENSION PROFILE NOT SPECIFIED ")
        if status == "Y":
            return APIResponses.success()
        elif message == "UNKNOWN PKI REQUEST":
            return APIResponses.not_found(message=message)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.failure(message=message)
