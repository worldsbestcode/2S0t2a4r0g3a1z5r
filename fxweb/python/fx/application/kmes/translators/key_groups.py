"""
@file      kmes/translators/key_groups.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators defined for the Key Groups method view
"""
from base.base_translator import BaseTranslator, SequentialTranslator
from kmes import kmes_parsers
from kmes.schemas import key_groups as KeyGroupsSchemas
from lib.utils import hapi_parsers as parsers
from lib.utils.hapi_excrypt_map import (
    DeviceKeyType,
    FWMajorKeySlot,
    FWSecUsage,
    GPKIKeyType,
    KeyGroupRetrievalMethod,
    KeyUsage,
)


class ListKeyGroups(BaseTranslator):
    """
    JSON to Excrypt map for retrieving pages of key groups
    """

    request_schema = KeyGroupsSchemas.ListKeyGroups()

    def __init__(self, server_interface):
        request_map = {
            "page": ("CH", lambda s: int(s) - 1),  # chunks start at 0, pages start at 1
            "pageCount": "CO",
            "parentId": "GI",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "CT": ("totalPages", int),
            "TO": ("totalItems", int),
            "GI": ("groups.id", parsers.parse_csv),
            "NA": ("groups.name", parsers.parse_csv),
            "CF": ("groups.numFolders", parsers.parse_csv_int),
            "CS": ("groups.numStores", parsers.parse_csv_int),
            "CO": ("groups.numKeys", parsers.parse_csv_int),
            "AL": ("groups.type", self.parse_group_type),
        }
        super().__init__(server_interface, "KeyGroups", "PGKG", request_map, response_map)

    def parse_group_type(self, csv):
        return [
            "store" if KeyGroupRetrievalMethod.enum_from_name(value).is_key_store() else "folder"
            for value in csv.split(",")
        ]

    def finalize_response(self, response):
        if response.setdefault("status", "Y") != "Y" or response.get("message"):
            return response

        response["currentPage"] = int(self.raw_request.get("page", 1))
        response["pageCount"] = int(self.raw_request.get("pageCount", 50))
        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        # Transpose/unpivot groups from dict of lists to list of dicts:
        response["groups"] = parsers.unpivot_dict(response["groups"])

        # Adjust because PGKG CF field is actually numFolders + numStores:
        for group in response["groups"]:
            group["numFolders"] -= group["numStores"]

        return response


class RetrieveKeyGroup(SequentialTranslator):
    """
    JSON to excrypt map for retrieving the permissions and info of a specified key group

    Calls RKVS to retrieve the key group, then calls RKPD to retrieve the permissions for it
    """

    request_schema = KeyGroupsSchemas.RetrieveKeyGroup()

    commands = [
        ("KeyGroups", "RKVS"),
        ("Misc", "RKPD"),
    ]

    request_maps = [
        {
            # RKVS:
            "id": "NA",
        },
        {
            # RKPD:
            "id": "NA",
            # "id": "ID",  # TODO(@dneathery): Update when RKVS supports UUIDs
            "_type": ("MN", "KEY_GROUP"),
        },
    ]

    response_maps = [
        {
            # RKVS:
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "PA": "parentId",
            "OW": "owner",
            "AD": "mailAddress",
            "RM": ("rotationPolicy.algorithm", KeyGroupRetrievalMethod.enum_from_value),
            "UP": (
                "rotationPolicy.rotationPeriod",
                lambda s: dict(zip(("period", "frequency"), s.split())),
            ),
            "TN": "keyPolicy.templateName",
            "KH": "keyPolicy.tr31Header",
            "KT": ("keyPolicy.keyType", DeviceKeyType.from_int),
            "CZ": "keyPolicy.keyUsage",
            "AS": ("keyPolicy.modifier", "0x{:>02X}".format),
            "MK": ("keyPolicy.majorKey", FWMajorKeySlot.value_to_name),
            "CT": ("keyPolicy.algorithm", GPKIKeyType.value_to_name),
            "SF": (
                "keyPolicy.clearExport",
                lambda s: FWSecUsage.eFWSecUsageClear in FWSecUsage(int(s, 16)),
            ),
        },
        {
            # RKPD:
            "AN": "status",
            "BB": "message",
            "PL": ("permissions", kmes_parsers.parse_mo_permissions),
        },
    ]

    def finalize_response(self, response):
        policy = response.get("keyPolicy", {})
        KeyUsage.symmetric_finalize(policy)

        rotation_algorithm = response.get("rotationPolicy", {}).get("algorithm")
        if not rotation_algorithm:
            pass
        elif rotation_algorithm.is_key_store():
            response["type"] = "store"
        else:
            response["type"] = "folder"
            response.pop("rotationPolicy")

        return response


class RetrieveKeyGroupPermissions(BaseTranslator):
    """
    JSON to excrypt map for retrieving the permissions of a specified key group
    """

    request_schema = KeyGroupsSchemas.RetrieveKeyGroupPermissions()

    def __init__(self, server_interface):
        fixed_values = {
            "MN": "KEY_GROUP",
        }
        request_maps = {
            "id": "ID",
            "name": "NA",
        }
        response_maps = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "ID": "id",
            "PL": (
                "permissions",
                kmes_parsers.parse_mo_permissions,
            ),
        }
        super().__init__(
            server_interface,
            "KeyGroups",
            "RKPD",
            request_maps,
            response_maps,
            fixed_values=fixed_values,
        )


class UpdateKeyGroupPermissions(BaseTranslator):
    """
    JSON to excrypt map to update the permissions of a specified key group
    """

    request_schema = KeyGroupsSchemas.UpdateKeyGroupPermissions()

    def __init__(self, server_interface):
        fixed_values = {
            "MN": "KEY_GROUP",
        }
        request_maps = {
            "id": "ID",
            "name": "NA",
            "permissions": (
                "PL",
                kmes_parsers.serialize_mo_permissions,
            ),
        }
        response_maps = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(
            server_interface,
            "KeyGroups",
            "RKPM",
            request_maps,
            response_maps,
            fixed_values=fixed_values,
        )


class DeleteKeyGroup(BaseTranslator):
    """
    JSON to Excrypt map for deleting a single key group
    """

    request_schema = KeyGroupsSchemas.DeleteKeyFolder()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "KeyGroups", "RKDS", request_map, response_map)


class CreateKeyFolder(SequentialTranslator):
    """
    JSON to Excrypt map for creating a key group as a key folder

    Calls RKCS to create a key folder, then calls RKPM to set the permissions for it
    """

    request_schema = KeyGroupsSchemas.CreateKeyFolder()

    commands = [
        ("KeyGroups", "RKCS"),
        ("Misc", "RKPM"),
    ]

    request_maps = [
        {
            # RKCS:
            "name": "NA",
            "parentId": "PA",
            "owner": "OW",
            "mailAddress": "AD",
        },
        {
            # RKPM:
            "name": "NA",
            # "id": "ID",  # TODO(@dneathery): Update when RKCS supports UUIDs
            "permissions": ("PL", kmes_parsers.serialize_mo_permissions),
            "_type": ("MN", "KEY_GROUP"),
        },
    ]

    response_maps = [
        {
            # RKCS:
            "AN": "status",
            "BB": "message",
            "ID": "id",
        },
        {
            # RKPM:
            "AN": "status",
            "BB": "message",
        },
    ]


class UpdateKeyFolder(SequentialTranslator):
    """
    JSON to Excrypt map for updating a key folder's properties
    """

    request_schema = KeyGroupsSchemas.UpdateKeyFolder()

    commands = [
        ("KeyGroups", "RKES"),
        ("Misc", "RKPM"),
    ]

    request_maps = [
        {
            # RKES:
            "id": "NA",  # TODO(@dneathery): Update when RKES supports UUIDs
            "newName": "NB",
            "owner": "OW",
            "mailAddress": "AD",
        },
        {
            # RKPM:
            "id": "NA",
            # "id": "ID",
            "permissions": ("PL", kmes_parsers.serialize_mo_permissions),
            "_type": ("MN", "KEY_GROUP"),
        },
    ]

    response_maps = [
        {
            # RKES:
            "AN": "status",
            "BB": "message",
        },
        {
            # RKPM:
            "AN": "status",
            "BB": "message",
        },
    ]

    def check_failure(self, response):
        # terminate early if there was an error in RKES or no permissions to change
        success = response.get("status", "N") == "Y" and not response.get("message")
        if success and "permissions" in self.raw_request:
            return None
        return response


class MoveKeyGroup(BaseTranslator):
    """
    JSON to Excrypt map for changing the parent of a single key group
    """

    request_schema = KeyGroupsSchemas.MoveKeyGroup()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "parentId": "PI",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "KeyGroups", "RKES", request_map, response_map)

    def preprocess_request(self, request):
        # If parentId is null, move group to top level. Indicated by sending tag with no value:
        if request.get("parentId", 0) is None:  # Falsy values ignored; make a truthy empty string:
            request["parentId"] = type("root", (), {"__str__": lambda s: ""})()
        return request


class RotateKeyStore(BaseTranslator):
    """
    JSON to Excrypt map for forcing a rotation on a key store
    """

    request_schema = KeyGroupsSchemas.RotateKeyStore()

    def __init__(self, server_interface):
        request_map = {
            "id": "KG",  # TODO(@dneathery): update when UUID / ID added to RKRG
            "expire": "EX",
            "generate": "NK",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "KN": "keyId",
        }
        super().__init__(server_interface, "KeyGroups", "RKRG", request_map, response_map)

    def preprocess_request(self, request):
        request["expire"] = "1"
        request["generate"] = "1"
        return request
