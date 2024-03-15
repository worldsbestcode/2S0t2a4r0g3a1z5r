"""
@file      kmes/translators/extension_profiles.py
@author    Dalton McGee(dmcgee@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for the KMES X.509 V3 Extension Profiles View
"""
from typing import List

import kmes.schemas.extension_profiles as schemas
from base.base_translator import BaseTranslator
from kmes.kmes_parsers import (
    parse_extension_descriptions,
    parse_extensions,
    parse_mo_permissions,
    serialize_extension_descriptions,
    serialize_extensions,
    serialize_mo_permissions,
)
from lib.utils import hapi_parsers as parsers
from lib.utils.hapi_excrypt_map import V3ExtensionModes


def split_extensions(combined: List[schemas.CombinedExtension]):
    """Split the extension map into extensions and descriptions
    Returns: a tuples of the extensions and descriptions
    """
    extensions = [ext.extension for ext in combined if ext.extension]
    descriptions = [desc.description for desc in combined]
    return extensions, descriptions


class CreateX509ExtensionProfile(BaseTranslator):
    """
    JSON to Excrypt to create single X.509 V3 Extension Profile
    """

    request_schema = schemas.CreateX509ExtensionProfile()

    def __init__(self, server_interface):
        request_map = {
            "name": "NA",
            "v3Extensions": ("EX", serialize_extensions),
            "_descriptions": ("ED", serialize_extension_descriptions),
            "allowUserDefined": ("UD", parsers.serialize_bool),
        }
        response_map = {"AN": "status", "BB": "message", "ID": "id"}
        super().__init__(server_interface, "ExtensionProfiles", "RAAE", request_map, response_map)

    def preprocess_request(self, request):
        extensions = request.get("v3Extensions")
        if extensions is not None:
            request["v3Extensions"], request["_descriptions"] = split_extensions(extensions)

        return request


class ListX509ExtensionProfiles(BaseTranslator):
    """
    JSON to Excrypt to retrieve single x.509 V3 Extension Profile
    """

    request_schema = schemas.ListX509ExtensionProfile()

    def __init__(self, server_interface):
        request_map = {"pageCount": "LN", "page": ("CN", lambda page: page - 1)}
        response_map = {
            "AN": "status",
            "BB": "message",
            "EN": ("names", parsers.parse_csv),
            "ID": ("id", parsers.parse_csv),
            "TO": ("totalItems", int),
            "CC": ("totalPages", int),
        }
        super().__init__(server_interface, "ExtensionProfiles", "RALE", request_map, response_map)

    def finalize_response(self, response):
        if not response.success:
            return response

        # Tags are missing if success but there are no results:
        response.setdefault("totalItems", 0)
        response.setdefault("totalPages", -1)
        response.setdefault("names", [])
        response.setdefault("id", [])

        response["currentPage"] = self.raw_request["page"]
        response["pageCount"] = self.raw_request["pageCount"]
        response["totalPages"] += 1
        response["v3Extensions"] = [
            {"name": response["names"][x], "id": response["id"][x]}
            for x in range(len(response["names"]))
        ]

        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        response.pop("id")
        response.pop("names")

        return response


class RetrieveX509ExtensionProfile(BaseTranslator):
    """
    JSON to Excrypt to retrieve single x.509 V3 Extension Profile
    """

    request_schema = schemas.RetrieveX509ExtensionProfile()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "ID": "id",
            "UD": ("allowUserDefined", parsers.parse_bool),
            "EX": ("v3Extensions", parse_extensions),
            "ED": ("_descriptions", parse_extension_descriptions),
        }
        super().__init__(server_interface, "ExtensionProfiles", "RAVE", request_map, response_map)

    def finalize_response(self, response):
        if not response.success:
            return response

        def format_extensions(extension):
            oid = extension["oid"]
            if oid in response["_descriptions"].keys():
                extension["mode"] = V3ExtensionModes.get_reverse(response["_descriptions"].pop(oid))

            return extension

        v3Extensions = list(map(format_extensions, response.get("v3Extensions", [])))

        # Add remaining descriptions
        if response.get("_descriptions", False):
            for key, value in response["_descriptions"].items():
                v3Extensions.append({"oid": key, "mode": V3ExtensionModes.get_reverse(value)})

        if "_descriptions" in response:
            del response["_descriptions"]

        response["v3Extensions"] = v3Extensions

        return response


class UpdateX509ExtensionProfile(BaseTranslator):
    """
    JSON to Excrypt to create single X.509 V3 Extension Profile
    """

    request_schema = schemas.UpdateX509ExtensionProfile()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "newName": "NN",
            "v3Extensions": ("EX", serialize_extensions),
            "_descriptions": ("ED", serialize_extension_descriptions),
            "allowUserDefined": ("UD", parsers.serialize_bool),
        }
        response_map = {"AN": "status", "BB": "message"}
        super().__init__(server_interface, "ExtensionProfiles", "RAEE", request_map, response_map)

    def preprocess_request(self, request):
        extensions = request.get("v3Extensions")
        if extensions is not None:
            request["v3Extensions"], request["_descriptions"] = split_extensions(extensions)

        return request


class DeleteX509ExtensionProfile(BaseTranslator):
    """
    JSON to Excrypt to delete single x.509 V3 Extension Profile
    """

    request_schema = schemas.DeleteX509ExtensionProfile()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
        }
        response_map = {"AN": "status", "BB": "message"}
        super().__init__(server_interface, "ExtensionProfiles", "RADE", request_map, response_map)


class RetrieveX509ExtensionPermissions(BaseTranslator):
    """
    JSON to Excrypt to retrieve single x.509 V3 Extension Profile"s Permissions
    """

    request_schema = schemas.RetrieveX509ExtensionPermissions()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "_type": "MN",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
            "NA": "name",
            "PL": ("permissions", parse_mo_permissions),
        }
        super().__init__(server_interface, "ExtensionProfiles", "RKPD", request_map, response_map)


class UpdateX509ExtensionPermissions(BaseTranslator):
    """
    JSON to Excrypt to update single x.509 V3 Extension Profile's Permissions
    """

    request_schema = schemas.UpdateX509ExtensionPermissions()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "_type": "MN",
            "permissions": ("PL", serialize_mo_permissions),
        }
        response_map = {"AN": "status", "BB": "message"}

        super().__init__(server_interface, "ExtensionProfiles", "RKPM", request_map, response_map)
