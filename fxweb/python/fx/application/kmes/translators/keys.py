"""
@file      kmes/translators/keys.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for KMES Keys views
"""

import lib.utils.hapi_excrypt_map as ExcryptMap
import lib.utils.hapi_parsers as parsers
from base.base_translator import BaseTranslator
from kmes.kmes_parsers import parse_securityusage, serialize_key_attributes, serialize_securityusage
from kmes.schemas import keys as KeySchemas


class CreateRandomKey(BaseTranslator):
    """
    JSON to Excrypt map for creating a Symmetric Key
    """

    request_schema = KeySchemas.CreateRandomKey()

    def __init__(self, server_interface):
        request_map = {
            "group": "KG",
            "groupId": "GI",
            "name": "KN",
            "type": ("TY", ExcryptMap.DeviceKeyType.to_int),
            "majorKey": ("FS", ExcryptMap.MajorKeys.get),
            "algorithm": ("CT", ExcryptMap.KeyAlgorithms.get),
            "keyUsage": "CZ",
            "securityUsage": ("SF", serialize_securityusage),
            "validityPeriod.start": "VS",
            "validityPeriod.end": "VE",
            "owner": "WN",
            "mailAddress": "AD",
            "attributes": ("AT", serialize_key_attributes),
            "tr31Header": "HE",
            "creationMode": "CM",
            "modifier": ("AS", "{:>02X}".format),
            "ksn": "KS",
            "ksnIncrement": "KI",
            # @TODO: Update once AKB Header tag is implemented
            # 'akbHeader': '',
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "AE": "checksum",
            "VT": "checksumAlgorithm",
            "ID": "id",
            "GI": "groupId",
            "BG": "keyblock",
        }

        super().__init__(server_interface, "Keys", "RKCK", request_map, response_map)

    def preprocess_request(self, request):
        # Ensure creation mode is set to "Generated"
        request["creationMode"] = 2

        # Map the key usage to the excrypt value
        ExcryptMap.KeyUsage.symmetric_preprocess(request)

        # Update key modifier based on key type
        request["modifier"] = ExcryptMap.DeviceKeyTypeModifier.get(request["type"], 0)

        return request


class ExportSymmetricKey(BaseTranslator):
    """
    JSON to Excrypt map for retrieving symmetric key info
    """

    request_schema = KeySchemas.ExportSymmetricKey()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "KN",
            "group": "KG",
            "groupId": "GI",
            "hostname": "HO",
            "transferKey": "HK",
            "format": ("FM", ExcryptMap.CryptogramExportType.get),
            "akbHeader": "HE",
            "useCbc": ("BC", lambda b: "Y" if b else "N"),
            "checksumLength": "AD",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
            "KN": "name",
            "KG": "group",
            "GI": "groupId",
            "BG": "keyBlock",
            "AE": "checksum",
            "KT": ("type", ExcryptMap.DeviceKeyType.from_int),
            "AS": ("modifier", "0x{:>02X}".format),
            "AT": ("attributes", parsers.parse_key_value_csv),
            "CZ": "keyUsage",
            "SF": ("securityUsage", parse_securityusage),
            "MK": ("majorKey", ExcryptMap.MajorKeys.get_reverse),
            "CT": ("algorithm", ExcryptMap.KeyAlgorithms.get_reverse),
            "TS": "validityPeriod.start",
            "TE": "validityPeriod.end",
            "CM": ("template", parsers.parse_bool),
            "VT": "checksumAlgorithm",
            # 'KM': 'state',
            # 'UP':('partial.uploaders', parsers.parse_csv),
            # 'EA': 'partial.finalChecksum',
            # 'TX': 'partial.expiration',
            # 'KP':('partial.numUploaded, int),
            # 'TP':('partial.numTotal, int),
            # 'KF':('partial.isFragment, parsers.parse_bool),
        }
        super().__init__(server_interface, "Keys", "RKRC", request_map, response_map)

    def finalize_response(self, response):
        # Update the key usage for symmetric keys
        ExcryptMap.KeyUsage.symmetric_finalize(response)
        return response


class DeleteTrustedKey(BaseTranslator):
    """
    JSON to Excrypt map for deleting a single trusted symmetric key
    """

    request_schema = KeySchemas.DeleteTrustedKey()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "KN",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "Keys", "RKDK", request_map, response_map)


class DeleteProtectedKey(BaseTranslator):
    """
    JSON to Excrypt map for deleting a single protected symmetric key
    """

    request_schema = KeySchemas.DeleteProtectedKey()

    def __init__(self, server_interface):
        request_map = {"id": "KI", "name": "NA", "_operation": "OP"}
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "Keys", "CLKY", request_map, response_map)


class CreateRandomProtectedKey(BaseTranslator):
    """
    JSON to Excrypt map for creating a Symmetric Protected Key
    """

    request_schema = KeySchemas.CreateRandomProtectedKey()

    def __init__(self, server_interface):
        request_map = {
            "operation": "OP",
            "groupId": "GI",
            "group": "KG",
            "name": "NA",
            "owner": "WN",
            "mailAddress": "AD",
            "validityPeriod.end": "VE",
            "validityPeriod.start": "VS",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "KI": "id",
        }

        super().__init__(server_interface, "Keys", "CLKY", request_map, response_map)

    def preprocess_request(self, request):
        # Ensure creation mode is set to "Generated"
        request["operation"] = "create"
        return request


class ImportKey(BaseTranslator):
    """
    JSON to Excrypt map for importing a Symmetric Key
    """

    request_schema = KeySchemas.ImportKey()

    def __init__(self, server_interface):
        request_map = {
            "algorithm": ("CT", ExcryptMap.KeyAlgorithms.get),
            "attributes": ("AT", serialize_key_attributes),
            "checksum": "AE",
            "checksumAlgorithm": "VT",
            "securityUsage": ("SF", serialize_securityusage),
            "creationMode": "CM",
            "keyBlock": "BG",
            "group": "KG",
            "groupId": "GI",
            "name": "KN",
            "type": ("TY", ExcryptMap.DeviceKeyType.to_int),
            "keyUsage": "CZ",
            "mailAddress": "AD",
            "majorKey": ("FS", ExcryptMap.MajorKeys.get),
            "modifier": ("AS", "{:>02X}".format),
            "owner": "WN",
            "tr31Header": "HE",
            "validityPeriod.end": "VE",
            "validityPeriod.start": "VS",
            # @TODO: Update once AKB Header tag is implemented
            # 'akbHeader': '',
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
        }

        super().__init__(server_interface, "Keys", "RKCK", request_map, response_map)

    def preprocess_request(self, request):
        # Ensure creation mode is set to "Import"
        request["creationMode"] = 0

        # Map the key usage to the excrypt value
        ExcryptMap.KeyUsage.symmetric_preprocess(request)

        # Update key modifier based on key type
        if "modifier" not in request:
            request["modifier"] = ExcryptMap.DeviceKeyTypeModifier.get(request["type"], 0)
        return request


class ExportSymmetricProtectedKey(BaseTranslator):
    """
    JSON to Excrypt map for retrieving symmetric protected key info
    """

    request_schema = KeySchemas.ExportSymmetricProtectedKey()

    def __init__(self, server_interface):
        request_map = {
            "id": "KI",
            "name": "NA",
            "transferKey": "WK",
            "transferKeyGroup": "WG",
            "format": ("FM", ExcryptMap.ProtectedKeyExportType.get),
            "randomPassphrase": ("MP", parsers.serialize_bool),
            "passphrase": "PW",
            "operation": ("OP", "export"),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "KI": "id",
            "KG": "group",
            "GI": "groupId",
            "BG": "keyBlock",
            "AE": "checksum",
            "CY": ("keyUsage", ExcryptMap.FWKeyUsage.asym_multi_usage_to_name),
            "KT": ("algorithm", ExcryptMap.KeyAlgorithmsV2.get_reverse),
            "VS": "validityPeriod.start",
            "VE": "validityPeriod.end",
        }
        super().__init__(server_interface, "Keys", "CLKY", request_map, response_map)


class RetrieveSymmetricProtectedKeyGroup(BaseTranslator):
    """
    JSON to Excrypt map for retrieving symmetric protected key info
    """

    request_schema = KeySchemas.RetrieveSymmetricProtectedKeyGroup()

    def __init__(self, server_interface):
        request_map = {
            "groupId": "GI",
            "group": "NA",
            "format": ("FM", ExcryptMap.ProtectedKeyRetrieveType.get),
            "randomPassphrase": ("MP", parsers.serialize_bool),
            "passphrase": "PW",
            "operation": "OP",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "KI": "id",
            "KG": "group",
            "GI": "groupId",
            "BG": "keyBlock",
            "AE": "checksum",
            "CY": ("keyUsage", ExcryptMap.KeyUsageMulti.get_reverse),
            "KT": ("algorithm", ExcryptMap.KeyAlgorithmsV2.get_reverse),
            "VS": "validityPeriod.start",
            "VE": "validityPeriod.end",
        }
        super().__init__(server_interface, "Keys", "CLGR", request_map, response_map)

    def preprocess_request(self, request):
        request["operation"] = "retrieve"
        return request
