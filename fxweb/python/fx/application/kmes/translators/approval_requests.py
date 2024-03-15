"""
@file      kmes/translators/approval_requests.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for Approval Requests
"""

from base.base_translator import BaseTranslator
from kmes.schemas import approval_requests as schemas
from lib.utils.hapi_excrypt_map import ApprovableObjectTypes, RevocationReasons
from lib.utils.hapi_parsers import (
    parse_csv,
    pivot_dict,
    serialize_bool,
    serialize_csv,
    unpivot_dict,
    vectorized,
)


class ListApprovalRequests(BaseTranslator):
    """
    JSON to Excrypt map for listing a Certificate Approval Requests
    """

    request_schema = schemas.ListApprovalRequests()

    def __init__(self, server_interface):
        request_map = {
            "approvalGroupId": "GI",
            "signed": ("IS", serialize_bool),
            "pending": ("IP", serialize_bool),
            "denied": ("ID", serialize_bool),
            "approved": ("IA", serialize_bool),
            "objectSigning": ("IO", serialize_bool),
            "x509": ("IX", serialize_bool),
            "page": ("CH", lambda page: page - 1),
            "pageCount": "CS",
            "format": ("FM", "1"),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "CC": ("totalPages", int),
            "CT": ("totalItems", int),
            "ID": ("requests.requestId", parse_csv),
            "NA": ("requests.name", parse_csv),
            "PI": ("requests.signingCertId", parse_csv),
            "PN": ("requests.signingCert", parse_csv),
            "OT": ("requests.type", parse_csv, vectorized(ApprovableObjectTypes.get)),
            "ST": ("requests.status", self.parse_st_tag),
        }

        super().__init__(server_interface, "ApprovalRequests", "RALX", request_map, response_map)

    @staticmethod
    def parse_st_tag(st):
        return pivot_dict(
            [
                {
                    "status": status.title(),
                    "approvals": int(approvals),
                    "approvalsRequired": int(required),
                }
                for entry in parse_csv(st)
                for status, approvals, required in (entry.split(":"),)
            ]
        )

    def finalize_response(self, response):
        if not response.success:
            return response

        # Move requests.status.status to requests.status
        # and requests.status.approvals to requests.approvals, etc.:
        response["requests"].update(response["requests"]["status"])
        response["requests"] = unpivot_dict(response["requests"])

        response["currentPage"] = self.raw_request["page"]
        response["pageCount"] = self.raw_request["pageCount"]

        if response["currentPage"] < response.get("totalPages", 0):
            response["nextPage"] = response["currentPage"] + 1

        return response


class DeleteApprovalRequest(BaseTranslator):
    """
    JSON to Excrypt map for updating a Certificate Approval Requests
    """

    request_schema = schemas.DeleteApprovalRequest()

    def __init__(self, server_interface):
        request_map = {
            "requestId": "ID",
        }
        response_map = {"AN": "status", "BB": "message"}

        super().__init__(server_interface, "ApprovalRequests", "RADX", request_map, response_map)


class ApproveDenyApprovalRequest(BaseTranslator):
    """
    JSON to Excrypt map for updating a Certificate Approval Requests
    """

    request_schema = schemas.ApproveDenyApprovalRequest()

    def __init__(self, server_interface):
        request_map = {
            "requestIds": ("ID", serialize_csv),
            "approve": ("AP", serialize_bool),
            "notes": "NT",
        }
        response_map = {"AN": "status", "BB": "message"}

        super().__init__(server_interface, "ApprovalRequests", "RAYX", request_map, response_map)

    def preprocess_request(self, request):
        if "requestId" in request:
            request.setdefault("requestIds", []).append(request["requestId"])
        return request


class RenewRequest(BaseTranslator):
    """
    JSON to Excrypt map for Renewing an X509 Approval Request
    """

    request_schema = schemas.RenewRequest()

    def __init__(self, server_interface):
        fixed_values = {"RE": 1}
        request_map = {
            "requestId": "ID",
            "ldapUsername": "LU",
            "ldapPassword": "LP",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "CE": "renewedCertificate",
        }

        super().__init__(
            server_interface, "ApprovalRequests", "RASX", request_map, response_map, fixed_values
        )


class RevokeRequest(BaseTranslator):
    """
    JSON to Excrypt map for Revoking an X509 Approval Request
    """

    request_schema = schemas.RevokeRequest()

    def __init__(self, server_interface):
        request_map = {
            "requestId": "ID",
            "reason": ("RT", RevocationReasons.to_items),
            "details": "RR",
            "ldapUsername": "LU",
            "ldapPassword": "LP",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "ApprovalRequests", "RASX", request_map, response_map)
