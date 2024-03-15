"""
@file      kmes/translators/pki_generation.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for PKI Generation Requests
"""

from binascii import unhexlify

from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding

from base.base_translator import BaseTranslator
from kmes.kmes_parsers import (
    parse_date,
    parse_extensions,
    parse_subject,
    serialize_date_time,
    serialize_extensions,
    serialize_subject,
)
from kmes.schemas import pki_generation as schemas
from kmes.translators.dn_profiles import RetrieveDNProfile
from lib.utils import hapi_excrypt_map as ExcryptMap
from lib.utils import hapi_parsers as parsers
from rk_host_application.rk_host_exceptions import FailedRAVD

from .approval_requests import ListApprovalRequests


class CreatePkiGenerationRequest(BaseTranslator):
    """
    JSON to Excrypt map for creating a PKI Request
    """

    request_schema = schemas.CreatePkiGenerationRequest()

    def __init__(self, server_interface):
        request_map = {
            "policyId": "ID",
            "pkiTree": "CA",
            "signingCert": "RT",
            "name": "NA",
            "hashType": ("HA", ExcryptMap.AsymHashTypes.get),
            "approvalGroup": "GN",
            "ldapUsername": "LU",
            "ldapPassword": "LP",
            "commonNameAsSan": ("NS", parsers.serialize_bool),
            "pkiOptions.extensionProfile": "EN",
            "pkiOptions.v3Extensions": ("EX", serialize_extensions),
            "keyOptions.modulus": ("KT", lambda m: f"RSA {m}"),
            "keyOptions.curve": ("KT", ExcryptMap.ECCCurveType.get),
            "pkiOptions.randomPassphrase": ("MP", parsers.serialize_bool),
            "pkiOptions.passphrase": "PW",
            "pkiOptions.subject": ("SN", serialize_subject),
            "pkiOptions.expiration": ("AF", serialize_date_time),
            "pkiOptions.savePkiKey": ("SK", parsers.serialize_bool),
            # 'pkiOptions.dnProfile' : makes RAVD call
            # 'pkiOptions.dnProfileId' : alternative, makes RAVD call
            # 'pkiOptions.exportPkcs12': makes RASX call
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "requestId",
            "AP": ("approvalsRemaining", int),
        }
        super().__init__(server_interface, "ApprovalRequests", "RAUP", request_map, response_map)

    def preprocess_request(self, request):
        options = request.get("pkiOptions", {})
        if not options:
            return request

        # If they supplied a DN profile, get that profile with RADV to set any missing RDNs
        subject_default = []
        if "dnProfileId" in options:
            subject_default = self.get_dn_profile(options["dnProfileId"], uuid=True)
        elif "dnProfile" in options:
            subject_default = self.get_dn_profile(options["dnProfile"], uuid=False)

        # If any OIDs are in the profile and not given in the subject, add them from the profile.
        # Explicitly supplied values replace profile's values. Preserve order if OID is the same.
        if subject_default:
            explicit_subject = options.setdefault("subject", [])
            explicit_oids = set(rdn["oid"] for rdn in explicit_subject)
            implicit_subject = [rdn for rdn in subject_default if rdn["oid"] not in explicit_oids]
            request["pkiOptions"]["subject"].extend(implicit_subject)

        return request

    def get_dn_profile(self, data, uuid):
        request = {"id": data} if uuid else {"name": data}
        response = RetrieveDNProfile(self.server_interface).translate(request)
        status = response.get("status", "N")
        if status != "Y":
            raise FailedRAVD(status, response.get("message", ""))
        return response.get("subject", [])

    def finalize_response(self, response):
        success = response.get("status", "N") == "Y"

        if success:
            request_id = self.raw_response.get("ID")

            # Return certId if savePkiKey was requested
            save_pki_key = self.raw_request.get("pkiOptions", {}).get("savePkiKey", False)

            if save_pki_key and request_id:
                response["certId"] = request_id

            # Export and return PKCS #12 if pkcs12 was requested, and 0 approvals remain
            export_pkcs12 = self.raw_request.get("pkiOptions", {}).get("exportPkcs12", False)
            remaining_approvals = response.get("approvalsRemaining")

            if export_pkcs12 and remaining_approvals == 0:
                # Retrieve user passphrase if supplied. Otherwise use generated passphrase
                passphrase = self.raw_request["pkiOptions"].get("passphrase", "")
                passphrase = self.raw_response.get("PW", passphrase)

                rasx_request = {
                    "ID": request_id,
                    "PW": passphrase,
                }
                rasx_response = self.server_interface.send_command(
                    "Approvals", "RASX", rasx_request
                )

                # Add PKCS #12 to response
                pkcs12 = rasx_response.get("PK", rasx_response.get("BB", "Unknown error"))
                rasx_status = rasx_response.get("AN", "N")

                if rasx_status == "Y":
                    response["pkcs12"] = pkcs12
                else:
                    response["status"] = rasx_status
                    response["message"] = pkcs12

        return response


class ListPkiGenerationRequests(ListApprovalRequests):
    """
    JSON to Excrypt map for listing PKI Generation Approval Requests
    """

    request_schema = schemas.ListPkiGenerationRequests()

    def preprocess_request(self, request):
        request["objectSigning"] = False
        return request


class RetrievePkiGenerationRequest(BaseTranslator):
    """
    JSON to Excrypt map for retrieving a PKI Request
    """

    request_schema = schemas.RetrievePkiGenerationRequest()

    def __init__(self, server_interface):
        request_map = {
            "requestId": "ID",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "ST": "signingStatus",
            "CN": "signingCert",
            "CP": ("approvals", int),
            "NP": ("approvalsRequired", int),
            "AP": ("approvalsRemaining", int),
            "HA": "hashType",
            "EN": "pkiOptions.extensionProfile",
            "AF": ("pkiOptions.expiration", parse_date),
            "SN": ("pkiOptions.subject", parse_subject),
            "EX": ("pkiOptions.v3Extensions", parse_extensions),
            "KT": "keyOptions",
            "CE": "certData",
            "PK": "pkcs12",
        }
        super().__init__(server_interface, "ApprovalRequests", "RAGP", request_map, response_map)

    def finalize_response(self, response):
        success = response.get("status", "N") == "Y"
        if not success:
            return response

        if self.raw_request["format"] == "PEM" and response.get("certData"):
            try:
                cert_data = x509.load_der_x509_certificate(unhexlify(response["certData"]))
                response["certData"] = cert_data.public_bytes(Encoding.PEM).decode("utf-8")
            except ValueError:
                response["message"] = "Failed to parse certificate data."

        key_type = response["keyOptions"]
        algorithm, val = key_type.split(" ")

        if algorithm == "ECC":
            field_name = "curve"
            val = ExcryptMap.ECCCurveNames.get(key_type)
        else:
            field_name = "modulus"
            val = int(val)

        response["keyOptions"] = {"algorithm": algorithm, field_name: val}
        return response


class UpdatePkiGenerationRequest(BaseTranslator):
    """
    JSON to Excrypt map for modifying a PKI issuance request
    """

    request_schema = schemas.UpdatePkiGenerationRequest()

    def __init__(self, server_interface):
        request_map = {
            "requestId": "ID",
            "newName": "NA",
            "hashType": ("HA", ExcryptMap.AsymHashTypes.get),
            "pkiOptions.expiration": ("AF", serialize_date_time),
            "pkiOptions.extensionProfile": "EN",
            "pkiOptions.passphrase": "PW",
            "pkiOptions.randomPassphrase": ("MP", parsers.serialize_bool),
            "pkiOptions.subject": ("SN", serialize_subject),
            "pkiOptions.v3Extensions": ("EX", serialize_extensions),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "ApprovalRequests", "RAEP", request_map, response_map)
