"""
@file      gcse_views.py
@author    Stephen Jackson (sjackson@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URIs for the GCSE views
"""

from app_sanitize import sanitize_request
from flask import g, request
from server_views import ServerTranslatedView

from lib.utils.google_response_generator import GAPIResponses, GAPIType


class GCSECommandView(ServerTranslatedView):
    """
    View class for google client side encryption(cse) commands
    """

    decorators = [sanitize_request]

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "GoogleCSE")

    def get(self, *args, **kwargs):
        """
        get base info of server
        """
        kacl_action = kwargs.get("csecommand", "")
        gcse_actions = ["status"]
        if kacl_action not in gcse_actions:
            http_response = GAPIResponses.invalid_argument(
                GAPIType.Cse, "Missing or unsupported command."
            )
        else:
            http_response = self.KACLStatus()

        return http_response

    def post(self, *args, **kwargs):
        """
        wrap and unwrap gcse keys
        """
        gcse_actions = ["wrap", "unwrap", "takeout_unwrap"]

        kacl_action = kwargs.get("csecommand", "")
        if kacl_action not in gcse_actions:
            http_response = GAPIResponses.invalid_argument(
                GAPIType.Cse, "Missing or unsupported command."
            )
        else:
            http_response = self.KACLWrapUnwrap(kacl_action)

        return http_response

    def KACLWrapUnwrap(self, kacl_action):

        request_data = request.get_json(force=True, silent=True)
        if not request_data:
            http_response = GAPIResponses.invalid_argument(
                GAPIType.Cse, "Missing data to perform wrapping."
            )
        else:
            token = request_data["authentication"]
            g.jwt = token
            request_data["action"] = kacl_action
            request_data["addAuthData"] = "Futurex"
            kacl_command = "GCSEUnwrap"
            if kacl_action == "wrap":
                kacl_command = "GCSEWrap"
                request_data["plaintext"] = request_data.pop("key", "")
            else:
                request_data["wrappedBlob"] = request_data.pop("wrapped_key", "")

            response = self.translate(kacl_command, request_data)
            if not response.get("status", "N") == "Y":
                message = response.get("message", "Missing message")
                error = GAPIResponses.get_error(message)
                http_response = GAPIResponses.error(GAPIType.Cse, error, message)
            else:
                frontend_response = {}
                if kacl_action == "wrap":
                    frontend_response["wrapped_key"] = response.get("wrappedBlob", "")
                else:
                    frontend_response["key"] = response.get("plaintext", "")

                http_response = GAPIResponses.success(frontend_response)

        return http_response

    def KACLStatus(self):
        response = {}
        response["server_type"] = "KACLS"
        response["vendor_id"] = "Futurex KACLS"
        response["version"] = "1.0.0"
        response["name"] = "VirtuCrypt KACL"

        return GAPIResponses.success(response)
