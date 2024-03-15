"""
@file      kmes/translators/object_signing.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for Object Signing Requests
"""

from base.base_translator import BaseTranslator
from kmes.schemas import object_signing as schemas
from lib.utils.hapi_excrypt_map import AsymHashTypes, SignaturePadding

from .approval_requests import ListApprovalRequests


class CreateObjSigningRequest(BaseTranslator):
    """
    JSON to Excrypt map for creating an Object Signature Approval Request.
    """

    request_schema = schemas.CreateObjSigningRequest()

    def __init__(self, server_interface):
        request_map = {
            "policyId": "ID",
            "pkiTree": "CA",
            "signingCert": "RT",
            "name": "NA",
            "hashType": ("HA", AsymHashTypes.get),
            "approvalGroup": "GN",
            "messageDigest": "RF",
            "paddingMode": ("ZA", SignaturePadding.get),
            "saltLength": "ZB",
            "ldapUsername": "LU",
            "ldapPassword": "LP",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "requestId",
            "AP": ("approvalsRemaining", int),
        }

        super().__init__(server_interface, "ApprovalRequests", "RAUO", request_map, response_map)


class ListObjSigningRequests(ListApprovalRequests):
    """
    JSON to Excrypt map for listing Object Signing Approval Requests
    """

    request_schema = schemas.ListObjSigningRequests()

    def preprocess_request(self, request):
        request["x509"] = False
        return request


class RetrieveObjSigningRequest(BaseTranslator):
    """
    JSON to Excrypt map for listing retrieving an Object Signing Approval Request.
    """

    request_schema = schemas.RetrieveObjSigningRequest()

    def __init__(self, server_interface):
        request_map = {"requestId": "ID"}
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "CA": "pkiTree",
            "ST": "signingStatus",
            "CN": "signingCert",
            "CP": ("approvals", int),
            "NP": ("approvalsRequired", int),
            "AP": ("approvalsRemaining", int),
            "HA": ("hashType", AsymHashTypes.get_reverse),
            "RF": "messageDigest",
            "ZA": ("paddingMode", SignaturePadding.get_reverse),
            "ZB": ("saltLength", int),
            "BO": "hashSignature",
        }

        super().__init__(server_interface, "ApprovalRequests", "RAGO", request_map, response_map)


class UpdateObjSigningRequest(BaseTranslator):
    """
    JSON to Excrypt map for updating an Object Signing Approval Request
    """

    request_schema = schemas.UpdateObjSigningRequest()

    def __init__(self, server_interface):
        request_map = {
            "requestId": "ID",
            "newName": "NA",
            "hashType": ("HA", AsymHashTypes.get),
            "messageDigest": "RF",
            "paddingMode": ("ZA", SignaturePadding.get),
            "saltLength": "ZB",
        }
        response_map = {"AN": "status", "BB": "message"}

        super().__init__(server_interface, "ApprovalRequests", "RAEO", request_map, response_map)
