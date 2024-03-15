"""
@file      kmes/translators/certificates.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for KMES Certificates views
"""

from binascii import unhexlify

from base_translator import BaseTranslator
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding

import kmes.schemas.certificates as CertificatesSchemas
import lib.utils.hapi_excrypt_map as ExcryptMap
import lib.utils.hapi_parsers as parsers
from kmes.kmes_parsers import (
    parse_mo_permissions,
    serialize_date_time,
    serialize_extensions,
    serialize_mo_permissions,
    serialize_securityusage,
    serialize_subject,
)


class CreateAlias(BaseTranslator):
    """
    JSON to Excrypt map for creating a certificate alias
    """

    request_schema = CertificatesSchemas.CreateAlias()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "RT",
            "alias": "AL",
            "pkiTree": "CA",
            "pkiTreeId": "AI",
        }
        response_map = {"AN": "status", "BB": "message"}

        super().__init__(server_interface, "Certificates", "RKGA", request_map, response_map)


class ListAliases(BaseTranslator):
    """
    JSON to Excrypt map for creating a certificate alias
    """

    request_schema = CertificatesSchemas.ListAliases()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "RT",
            "alias": "AL",
            "pkiTree": "CA",
            "pkiTreeId": "AI",
        }
        response_map = {"AN": "status", "BB": "message", "AL": ("aliases", parsers.parse_csv)}

        super().__init__(server_interface, "Certificates", "RKRA", request_map, response_map)


class DeleteAlias(BaseTranslator):
    """
    JSON to Excrypt map for deleting a certificate alias
    """

    request_schema = CertificatesSchemas.DeleteAlias()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "alias": "AL",
            "pkiTree": "CA",
            "pkiTreeId": "AI",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "Certificates", "RKDA", request_map, response_map)


class CreateX509(BaseTranslator):
    """
    JSON to Excrypt map for creating a certificate with a generated key pair
    """

    request_schema = CertificatesSchemas.CreateX509()

    def __init__(self, server_interface):
        request_map = {
            "parent": "RH",
            "parentId": "PI",
            "pkiTree": "CA",
            "pkiTreeId": "AI",
            "alias": "AL",
            "pkiOptions.hashType": ("RG", ExcryptMap.RKGCHashTypes.name_to_value),
            "pkiOptions.subject": ("SN", serialize_subject),
            "pkiOptions.v3Extensions": ("XW", serialize_extensions),
            "pkiOptions.validityPeriod.end": ("AF", serialize_date_time),
            "pkiOptions.validityPeriod.start": ("BF", serialize_date_time),
            "keyOptions.securityUsage": ("SF", serialize_securityusage),
            "keyOptions.majorKey": ("FS", ExcryptMap.MajorKeys.get),
            "keyOptions.keyUsage": ("CZ", ExcryptMap.KeyUsage.Asymmetric.get),
            "keyOptions.algorithm": ("KT", {"RSA": 1, "ECC": 2}.get),
            "keyOptions.exponent": "RA",
            "keyOptions.modulus": "RB",
            "keyOptions.curve": ("RA", ExcryptMap.ECCCurveId.name_to_value),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
            "RV": "certificateData",
            "PV": "privateKey",
        }
        super().__init__(server_interface, "Certificates", "RKGC", request_map, response_map)

    def serialize_constraints(self, constraints):
        ca = constraints.get("ca")
        pathlen = constraints.get("pathLength")
        critical = constraints.get("critical")

        result = "CA:true" if ca else "CA:false"
        if ca and pathlen is not None:
            result += f",pathlen:{pathlen}"
        if critical:
            result = "critical," + result
        return result


class RetrieveCertificate(BaseTranslator):
    """
    JSON to Excrypt map for retrieving a certificate
    """

    request_schema = CertificatesSchemas.RetrieveCertificate()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "RT",
            "alias": "AL",
            "pkiTree": "CA",
        }
        fixed_values = {
            "EF": "2",  # Set export mode to "no export"
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "AI": "pkiTreeId",
            "PI": "parentId",
            "RI": "policyId",
            "ID": "id",
            "RT": "name",
            "TY": ("type", ExcryptMap.PkiCertType.from_typeToStr),
            "LD": "loadTime",
            "ST": ("certStatus", str.title),  # Valid, Pending, or Revoked (NOT signing status)
            "AR": ("archived", parsers.parse_bool),
            "RA": "revocation.action",
            "RR": "revocation.reason",
            "CY": ("keyOptions.keyUsage", ExcryptMap.FWKeyUsage.asym_multi_usage_to_name),
            "FS": ("keyOptions.majorKey", ExcryptMap.FWMajorKeySlot.value_to_name),
        }

        super().__init__(
            server_interface, "Certificates", "RKRK", request_map, response_map, fixed_values
        )


class ExportCertificate(BaseTranslator):
    """
    JSON to Excrypt map for exporting a Certificate
    """

    request_schema = CertificatesSchemas.ExportCertificate()

    def __init__(self, server_interface):
        fixed_values = {
            "EF": "0",
        }
        request_map = {
            "pkiTree": "CA",
            "id": "ID",
            "name": "RT",
            "alias": "AL",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "RV": "certData",
        }

        super().__init__(
            server_interface, "Certificates", "RKRK", request_map, response_map, fixed_values
        )

    def finalize_response(self, response):
        # Convert hex-encoded DER to PEM
        if "certData" in response:
            _format = self.raw_request["format"]
            if _format != "JSON":
                extension = "der"
                cert_data = unhexlify(response["certData"])

                if _format != "DER":
                    extension = "pem"
                    try:
                        _cert_data = x509.load_der_x509_certificate(cert_data)
                        cert_data = _cert_data.public_bytes(Encoding.PEM)
                    except ValueError:
                        response["message"] = "Failed to parse certificate data."

                response["certData"] = cert_data
                # Default filename to X509_Certificate
                filename = "X509_Certificate"

                # Update filename is filename, alias, or name is provided
                if "filename" in self.raw_request:
                    filename = self.raw_request.get("filename")
                elif "alias" in self.raw_request:
                    filename = self.raw_request.get("alias")
                elif "name" in self.raw_request:
                    filename = self.raw_request.get("name")

                response["filename"] = filename + "." + extension

        return response


class DeleteCertificate(BaseTranslator):
    """
    JSON to Excrypt map for deleting a single certificate
    """

    request_schema = CertificatesSchemas.DeleteCertificate()

    def __init__(self, server_interface):
        request_map = {
            "alias": "AL",
            "name": "RT",
            "id": "ID",
            "pkiTree": "CA",
            "pkiTreeId": "AI",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "Certificates", "RKDC", request_map, response_map)


class ArchiveRestore(BaseTranslator):
    """
    JSON to Excrypt map for generating an EMV ICC Certificate
    """

    request_schema = CertificatesSchemas.ArchiveRestore()

    def __init__(self, server_interface):
        request_map = {
            "_operation": "OP",
            "pkiTreeId": "AI",
            "parentId": "PI",
            "childrenOnly": ("LF", parsers.serialize_bool),
            # "jsonFilter": "FI", TODO: uncomment when feature implemented
            "applyToAll": ("EA", parsers.serialize_bool),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "Certificates", "CERT", request_map, response_map)


class GenerateEmvCert(BaseTranslator):
    """
    JSON to Excrypt map for generating an EMV ICC Certificate
    """

    request_schema = CertificatesSchemas.GenerateEmvCert()

    def __init__(self, server_interface):
        request_map = {
            "pkiTree": "CA",
            "name": "RH",
            "alias": "AL",
            "exponent": "RA",
            "modulus": "RB",
            "certOne.pan": "EA",
            "certOne.expiration": "EB",
            "certOne.sda": "EC",
            "certTwo.pan": "FA",
            "certTwo.expiration": "FB",
            "certTwo.sda": "FC",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "SD": "publicKey",
            "PV": "privateKey",
            "EF": "certOne.data",
            "FF": "certTwo.data",
        }

        super().__init__(server_interface, "Certificates", "RKEC", request_map, response_map)


class ImportEMV(BaseTranslator):
    """
    JSON to Excrypt map for importing an EMV certificate
    """

    request_schema = CertificatesSchemas.ImportEMV()

    def __init__(self, server_interface):
        request_map = {
            "data": "RV",
            "keyOptions.keyUsage": ("CZ", ExcryptMap.KeyUsage.Asymmetric.get),
            "keyOptions.majorKey": ("FS", ExcryptMap.MajorKeys.get),
            "name": "RT",
            "parent": "RH",
            "parentId": "PI",
            "pkiTree": "CA",
            "pkiTreeId": "AI",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
        }

        super().__init__(server_interface, "Certificates", "RKIC", request_map, response_map)


class ImportX509(BaseTranslator):
    """
    JSON to Excrypt map for importing an X.509 certificate
    """

    request_schema = CertificatesSchemas.ImportX509()

    def __init__(self, server_interface):
        request_map = {
            "data": "RV",
            "keyOptions.keyUsage": ("CZ", ExcryptMap.KeyUsage.Asymmetric.get),
            "keyOptions.majorKey": ("FS", ExcryptMap.MajorKeys.get),
            "parent": "RH",
            "parentId": "PI",
            "pkiTree": "CA",
            "pkiTreeId": "AI",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
        }

        super().__init__(server_interface, "Certificates", "RKIC", request_map, response_map)


class RetrieveCertPermissions(BaseTranslator):
    """
    JSON to Excrypt map for viewing the permissions of a single certificate
    """

    request_schema = CertificatesSchemas.RetrieveCertPermissions()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "pkiTree": "GN",
            "_type": "MN",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "ID": "id",
            "PL": ("permissions", parse_mo_permissions),
        }

        super().__init__(server_interface, "Certificates", "RKPD", request_map, response_map)

    def preprocess_request(self, request):
        request["_type"] = "X509CERT"
        return request


class UpdateCertPermissions(BaseTranslator):
    """
    JSON to Excrypt map for updating the permissions of a single certificate
    """

    request_schema = CertificatesSchemas.UpdateCertPermissions()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "pkiTree": "GN",
            "_type": "MN",
            "permissions": ("PL", serialize_mo_permissions),
            "updateChildren": ("RE", ExcryptMap.PermissionScope.name_to_value),
            # TODO(@dmcgee): update when implicit field added to RKPM
        }
        response_map = {"AN": "status", "BB": "message"}

        super().__init__(server_interface, "Certificates", "RKPM", request_map, response_map)

    def preprocess_request(self, request):
        request["_type"] = "X509CERT"
        return request
