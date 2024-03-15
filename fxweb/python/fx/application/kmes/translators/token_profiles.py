"""
@file      kmes/translators/token_profiles.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators defined for the token group profile views
"""

import kmes.schemas.token_profiles as schemas
from base.base_translator import BaseTranslator
from kmes import kmes_parsers
from lib.utils import hapi_parsers as parsers
from lib.utils.hapi_excrypt_map import DUKPTTypes, FpeAlgorithm
from lib.utils.string_utils import from_hex, to_hex

from .shared import ObjectLookupTranslator


class CreateTokenProfile(BaseTranslator):
    """
    JSON to Excrypt map for creating token profiles
    """

    request_schema = schemas.CreateTokenProfile()

    def __init__(self, server_interface):
        request_map = {
            "algorithm": ("AA", FpeAlgorithm.to_int),
            "keyId": "KI",
            "luhnCheck": ("LU", parsers.serialize_bool),
            "name": "TG",
            "paddingLength": "ML",
            "prefix": "SL",
            "preserveLeading": "PL",
            "preserveTrailing": "PT",
            "namespace": ("AB", to_hex),
            "verificationLength": "VL",
            "cipher": "BJ",
            "ivMode": "ZA",
            "ivSize": "GH",
            "reversible": ("RT", parsers.serialize_bool),
            "inputValidation": "IM",
            "outputRegex": ("OR", to_hex),
            "inputRegex": ("IR", to_hex),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
        }
        super().__init__(server_interface, "TokenProfiles", "TKGA", request_map, response_map)


class ListTokenProfiles(ObjectLookupTranslator):
    """
    JSON to Excrypt map for listing token profiles
    """

    type_enum = "TOKENGROUP"
    type_name = "tokenProfiles"
    parent_name = None
    container_name = None


class RetrieveTokenProfile(BaseTranslator):
    """
    JSON to Excrypt map to Retrieve a token profile
    """

    request_schema = schemas.RetrieveTokenProfile()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "TG": "name",
            "ID": "id",
            "KI": "keyId",
            "AA": ("algorithm", FpeAlgorithm.from_typeToStr),
            "VL": ("verificationLength", int),
            "LU": ("luhnCheck", parsers.parse_bool),
            "ML": ("paddingLength", int),
            "SL": "prefix",
            "BJ": "cipher",
            "ZA": "ivMode",
            "GH": ("ivSize", int),
            "RT": ("reversible", parsers.parse_bool),
            "IM": "inputValidation",
            "OR": ("outputRegex", from_hex),
            "IR": ("inputRegex", from_hex),
            "PL": ("preserveLeading", int),
            "PT": ("preserveTrailing", int),
            "AB": ("namespace", from_hex),
        }

        super().__init__(server_interface, "TokenProfiles", "TKGG", request_map, response_map)


class UpdateTokenProfiles(BaseTranslator):
    """
    JSON to Excrypt map to Update a single token profile
    """

    request_schema = schemas.UpdateTokenProfile()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "TG",
            "newName": "TB",
            "keyId": "KI",
            "keyGroup": "KG",
            "verificationLength": "VL",
            "luhnCheck": ("LU", parsers.serialize_bool),
            "paddingLength": "ML",
            "prefix": "SL",
            "preserveLeading": "PL",
            "preserveTrailing": "PT",
            "cipher": "BJ",
            "ivMode": "ZA",
            "ivSize": "GH",
            "reversible": ("RT", parsers.serialize_bool),
            "inputValidation": "IM",
            "outputRegex": ("OR", to_hex),
            "inputRegex": ("IR", to_hex),
            "namespace": ("AB", to_hex),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "TokenProfiles", "TKGU", request_map, response_map)


class DeleteTokenProfile(BaseTranslator):
    """
    JSON to Excrypt map for deleting a token profile
    """

    request_schema = schemas.DeleteTokenProfile()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "TokenProfiles", "TKGD", request_map, response_map)


class RetrievePermissions(BaseTranslator):
    """
    JSON to Excrypt map for viewing the permissions of a single token group
    """

    request_schema = schemas.RetrievePermissions()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "_type": ("MN", "TOKENGROUP"),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "ID": "id",
            "PL": ("permissions", kmes_parsers.parse_mo_permissions),
        }

        super().__init__(server_interface, "TokenProfiles", "RKPD", request_map, response_map)


class UpdatePermissions(BaseTranslator):
    """
    JSON to Excrypt map for updating the permissions of a single token group
    """

    request_schema = schemas.UpdatePermissions()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "_type": ("MN", "TOKENGROUP"),
            "permissions": ("PL", kmes_parsers.serialize_mo_permissions),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "TokenProfiles", "RKPM", request_map, response_map)


class Tokenize(BaseTranslator):
    """
    JSON to Excrypt map to Tokenize data
    """

    request_schema = schemas.Tokenize()

    def __init__(self, server_interface):
        request_map = {
            "data": ("BO", to_hex),
            "profile.id": "ID",
            "profile.name": "TG",
            "cardholderProfile.id": "VP",
            "cardholderProfile.name": "TH",
            "keyGroup.id": "GI",
            "keyGroup.name": "KG",
            "key.id": "KI",
            "key.name": "KN",
            "ksn": "KS",
            "dukptVariant": ("FS", DUKPTTypes.get),
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "BO": ("token", from_hex),
            "KY": "key.name",
        }
        super().__init__(server_interface, "TokenProfiles", "TOKA", request_map, response_map)


class Detokenize(BaseTranslator):
    """
    JSON to Excrypt map to Detokenize a token
    """

    request_schema = schemas.Detokenize()

    def __init__(self, server_interface):
        request_map = {
            "token": ("BO", to_hex),
            "profile.id": "ID",
            "profile.name": "TG",
            "cardholderProfile.id": "VP",
            "cardholderProfile.name": "TH",
            "key.id": "KI",
            "key.name": "KY",
            "verifyOnly": ("VF", parsers.serialize_bool),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "BO": ("data", from_hex),
            "KY": "key.name",
        }
        super().__init__(
            server_interface,
            "TokenProfiles",
            "TOKG",
            request_map,
            response_map,
        )
