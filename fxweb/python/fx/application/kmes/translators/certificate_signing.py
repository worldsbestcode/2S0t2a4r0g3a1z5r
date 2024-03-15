"""
@file      kmes/translators/certificate_signing.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for Certificate Signing Requests
"""

from base.base_translator import BaseTranslator
from kmes.kmes_parsers import (
    parse_date,
    parse_extensions,
    parse_subject,
    serialize_date_time,
    serialize_extensions,
    serialize_subject,
)
from kmes.schemas import certificate_signing as schemas
from lib.utils.hapi_excrypt_map import AsymHashTypes, ECCCurveNames

from .approval_requests import ListApprovalRequests


class CreateCertSigningRequest(BaseTranslator):
    """
    JSON to Excrypt map for creating one Certificate Signing Request
    """

    request_schema = schemas.CreateCertSigningRequest()

    def __init__(self, server_interface):
        request_map = {
            "policyId": "ID",
            "pkiTree": "CA",
            "signingCert": "RT",
            "name": "NA",
            "hashType": ("HA", AsymHashTypes.get),
            "approvalGroup": "GN",
            "signingRequest": "CR",
            "pkiOptions.extensionProfile": "EN",
            "pkiOptions.expiration": ("AF", serialize_date_time),
            "pkiOptions.subject": ("SN", serialize_subject),
            "pkiOptions.v3Extensions": ("EX", serialize_extensions),
            "ldapUsername": "LU",
            "ldapPassword": "LP",
        }
        response_map = {"AN": "status", "BB": "message", "ID": "requestId"}

        super().__init__(server_interface, "ApprovalRequests", "RAUX", request_map, response_map)


class ListCertSigningRequests(ListApprovalRequests):
    """
    JSON to Excrypt map for listing Certificate Signing Requests
    """

    request_schema = schemas.ListCertSigningRequests()

    def preprocess_request(self, request):
        request["objectSigning"] = False
        return request


class RetrieveCertSigningRequest(BaseTranslator):
    """
    JSON to Excrypt map for retrieving one Certificate Signing Request
    """

    request_schema = schemas.RetrieveCertSigningRequest()

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
            "HA": "hashType",
            "CR": "signingRequest",
            "CE": "certData",
            "EN": "pkiOptions.extensionProfile",
            "AF": ("pkiOptions.expiration", parse_date),
            "SN": ("pkiOptions.subject", parse_subject),
            "EX": ("pkiOptions.v3Extensions", parse_extensions),
            "KT": "keyOptions",
        }
        super().__init__(server_interface, "ApprovalRequests", "RAGX", request_map, response_map)

    def finalize_response(self, response):
        success = response.get("status", "N") == "Y"
        if not success:
            return response

        key_type = response["keyOptions"]
        algorithm, val = key_type.split(" ")

        if algorithm == "ECC":
            field_name = "curve"
            val = ECCCurveNames.get(key_type)
        else:
            field_name = "modulus"
            val = int(val)

        response["keyOptions"] = {"algorithm": algorithm, field_name: val}
        return response


class UpdateCertSigningRequest(BaseTranslator):
    """
    JSON to Excrypt map for updating one Certificate Signing Request
    """

    request_schema = schemas.UpdateCertSigningRequest()

    def __init__(self, server_interface):
        request_map = {
            "requestId": "ID",
            "newName": "NA",
            "hashType": ("HA", AsymHashTypes.get),
            "signingRequest": "CR",
            "pkiOptions.extensionProfile": "EN",
            "pkiOptions.expiration": ("AF", serialize_date_time),
            "pkiOptions.subject": ("SN", serialize_subject),
            "pkiOptions.v3Extensions": ("EX", serialize_extensions),
        }
        response_map = {"AN": "status", "BB": "message"}

        super().__init__(server_interface, "ApprovalRequests", "RAEX", request_map, response_map)
