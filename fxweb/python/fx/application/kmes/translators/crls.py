"""
@file      kmes/translators/crls.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for Certificate Revocation Lists
"""

from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding

import kmes.schemas.crls as schemas
from base.base_translator import BaseTranslator
from lib.utils.hapi_excrypt_map import RevocationReasons


class BaseCrl(BaseTranslator):
    """
    Base Translator for all CRL Translator Classes
    """

    request_schema = schemas.CreateCrl()

    def __init__(self, server_interface):
        request_map = {
            "_operation": "OP",
            "certId": "ID",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(
            server_interface, "CertificateRevocationLists", "RKRL", request_map, response_map
        )


class CreateCrl(BaseCrl):
    """
    JSON to Excrypt map for creating one Certificate Revocation List
    """

    request_schema = schemas.CreateCrl()

    def __init__(self, server_interface):
        super().__init__(server_interface)

        self.request_map.update(
            {
                "hashType": "RG",
                "interval": "IC",
                "intervalUnit": "CP",
                "overlap": "OI",
                "overlapUnit": "OR",
            }
        )

    def preprocess_request(self, request):
        request["_operation"] = "create"
        return request


class RetrieveCrl(BaseCrl):
    """
    JSON to Excrypt map for retrieving one Certificate Revocation List
    """

    request_schema = schemas.RetrieveCrl()

    def __init__(self, server_interface):
        super().__init__(server_interface)

        self.response_map.update(
            {
                "RV": ("revision", int),
                "RG": "hashType",
                "IC": ("interval", int),
                "CP": "intervalUnit",
                "OI": ("overlap", int),
                "OR": "overlapUnit",
                "LU": "lastUpdateTime",
                "NU": "nextUpdateTime",
                "NR": ("numberRevoked", int),
            }
        )

    def preprocess_request(self, request):
        request["_operation"] = "get"
        return request


class UpdateCrl(CreateCrl):
    """
    JSON to Excrypt map for updating one Certificate Revocation List
    Inherits from 'CreateCrl' directly because they other identical other than '_operation'
    """

    request_schema = schemas.UpdateCrl()

    def preprocess_request(self, request):
        request["_operation"] = "set"
        return request


class DeleteCrl(BaseCrl):
    """
    JSON to Excrypt map for deleting one Certificate Revocation List
    """

    request_schema = schemas.DeleteCrl()

    def preprocess_request(self, request):
        request["_operation"] = "delete"
        return request


class ExportCrl(BaseTranslator):
    """
    JSON to Excrypt map for exporting one Certificate Revocation List
    """

    request_schema = schemas.ExportCrl()

    def __init__(self, server_interface):
        request_map = {
            "certId": "ID",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "BO": "data",
        }

        # Similar to `ImportCrl`, implements `_internal_RKRL_download` to return chunked data
        # as a single string as opposed to a series to be concatanated later by the end-user.
        super().__init__(
            server_interface,
            "CertificateRevocationLists",
            "_internal_RKRL_download",
            request_map,
            response_map,
            {"OP": "download"},
        )

    def preprocess_request(self, request):
        """
        Stores request variables to be passed to response as they're not returned from RKClient.
        """
        self._format = request.get("format", None)
        self._filename = request.get("filename", None)
        self._certId = request.get("certId")
        return request

    def finalize_response(self, response):
        if not response.success:
            return response

        try:
            if self._format == "PEM" or self._format is None:
                cert = x509.load_der_x509_crl(bytes.fromhex(response["data"]))
                # this is decoded to UTF-8 because bytes data can't be JSONified.
                response["data"] = cert.public_bytes(Encoding.PEM).decode("utf-8")
        except ValueError:
            pass

        filename = self._filename  # this keeps the next line under 100 characters.
        response["filename"] = f"{self._certId[1:-1]}" if filename is None else filename
        response["format"] = self._format
        return response


class ImportCrl(BaseTranslator):
    """
    JSON to Excrypt map for importing one Certificate Revocation List
    """

    request_schema = schemas.ImportCrl()

    def __init__(self, server_interface):
        request_map = {
            "certId": "ID",
            "data": "BO",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        # Uses custom command `_internal_RKRL_add` in `rk_host_commands` to chunk data
        # and send as to avoid Python's recursion limit. Looping over the chunks would've been
        # overly complicated to implement with BaseTranslator's hooks.
        super().__init__(
            server_interface,
            "CertificateRevocationLists",
            "_internal_RKRL_add",
            request_map,
            response_map,
            {"OP": "add"},
        )


class RevokeCert(BaseCrl):
    """
    JSON to Excrypt map for revoking one Certificate using a CRL
    """

    request_schema = schemas.RevokeCert()

    def __init__(self, server_interface):
        super().__init__(server_interface)

        self.request_map.update(
            {
                "certId": "ID",
                "revokeCertId": "AD",
                "reason": ("RR", RevocationReasons.to_items),
                "action": "RA",
            }
        )

    def preprocess_request(self, request):
        request["_operation"] = "revoke"
        return request
