"""
@file      kmes/views/approval_requests.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for Approval Requests
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses


class ApprovalReq(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ApprovalRequests")

    def get(self):
        request_data = request.args.to_dict(flat=True)

        response = self.translate("ListRequests", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif message == "INVALID CHUNK":
            return APIResponses.not_found(message="Page out of range")
        else:
            return APIResponses.bad_request(message=message)

    def delete(self):
        request_data = request.args
        response = self.translate("DeleteRequest", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)


class ApproveRequest(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ApprovalRequests")

    def put(self):
        request_data = request.get_json()
        request_data["approve"] = True

        response = self.translate("ApproveDenyRequest", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)


class DenyRequest(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ApprovalRequests")

    def put(self):
        request_data = request.get_json()
        request_data["approve"] = False

        response = self.translate("ApproveDenyRequest", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message)


class RenewRequest(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ApprovalRequests")

    def post(self):
        request_data = request.get_json()

        response = self.translate("Renew", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif "SIGNED REQUESTS ONLY" in message:
            return APIResponses.conflict(message)
        elif "INVALID" in message:
            return APIResponses.bad_request(message)
        elif "UNKNOWN" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.failure(message)


class RevokeRequest(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "ApprovalRequests")

    def put(self):
        request_data = request.get_json()

        response = self.translate("Revoke", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        elif "SIGNED REQUESTS ONLY" in message:
            return APIResponses.conflict(message)
        elif "INVALID" in message:
            return APIResponses.bad_request(message)
        elif "UNKNOWN" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.failure(message)
