"""
@file      kmes/translators/shared.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
General translators defined for the use amongst multiple URIs
"""
import abc

import lib.utils.hapi_excrypt_map as ExcryptMap
from base.base_translator import BaseTranslator
from kmes.schemas import shared_schemas
from lib.utils import hapi_parsers as parsers
from lib.utils.string_utils import hex_to_uuid, is_uuid


class PermissionDescriptionTranslator(BaseTranslator):
    """
    Retrieve permission string mappings for use by front-end to display human readable strings.
    """

    # TODO(@dneathery): update when RKPS command finalized
    def __init__(self, server_interface):
        # request_map can be 'types' (Log, User...) or 'flags' (Add, Delete...)
        request_map = {"map_type": "FN"}
        response_map = {
            "TY": ("names", parsers.parse_csv),
            "DS": ("descriptions", parsers.parse_csv),
        }
        super().__init__(server_interface, "Permissions", "RKPS", request_map, response_map)

    def finalize_response(self, response):
        try:
            response = dict(zip(response["names"], response["descriptions"]))
        except (TypeError, KeyError):
            response = {}
        return response


class ObjectLookupTranslator(abc.ABC, BaseTranslator):
    """
    Base class for JSON to Excrypt maps for listing managed objects with RKLN
    """

    # Override class attributes:
    type_name = "unknown"  # Name for object type in response field
    type_enum = "UNKNOWN"  # Remotekey enum ManagedObject::TYPE, for "MN" tag
    parent_name = "parent"  # Enables parentId field, and return parents in response
    container_name = "container"  # Enables containerId field
    column_names = {  # Displayable->table column names for filter value to match against
        "Name": "name"
    }

    def __init__(self, server_interface):
        super().__init__(server_interface, "Misc", "RKLN", self.request_map, self.response_map)

    def __init_subclass__(cls, **kwargs):
        cls.request_schema = shared_schemas.ObjectLookup(
            name=cls.type_name,
            columns=cls.column_names,
            parent=cls.parent_name,
            container=cls.container_name,
        )
        cls.request_map = {
            "type": ("MN", str.upper),
            "page": ("CH", lambda s: int(s) - 1),  # chunks start at 0, pages start at 1
            "pageCount": "CS",
            "includeArchived": ("AR", parsers.serialize_bool),
            "nameMatch": "IN",
            # TODO(@dneathery): Update when Unique IDs added to RKLN:
            f"{cls.container_name}Name": "GN",
            f"{cls.parent_name}Name": "PN",
            f"{cls.parent_name}Alias": "AJ",
            "includeParent": ("LG", parsers.serialize_bool),
        }
        cls.filter_map = {
            "operator": ("A", ExcryptMap.FilterClauseOperator.name_to_value),
            "attribute": ("B", cls.column_names.get),
            "match": ("C", ExcryptMap.FilterClauseMatch.name_to_value),
            "value": "D",
            "rangeMin": "E",
            "rangeMax": "F",
            "clause": "G",
            "negate": ("H", parsers.serialize_bool),
        }
        cls.response_map = {
            "AN": "status",
            "BB": "message",
            "CT": ("totalPages", int),
            "TO": ("totalItems", int),
            "CS": ("pageCount", int),
            "GL": (f"{cls.type_name}.{cls.parent_name}Name", parsers.parse_csv),
            "NA": (f"{cls.type_name}.name", parsers.parse_csv),
            "ID": (f"{cls.type_name}.id", parsers.parse_csv),
            "AL": (f"{cls.type_name}.alias", parsers.parse_csv),
        }

    def preprocess_request(self, request):
        request["type"] = self.type_enum
        request["includeParent"] = bool(self.parent_name)
        return request

    def translateRequest(self, request):
        result = super().translateRequest(request)
        # Translate the filters separately as they are dynamic 'filter[0].operator' -> 'ZA'
        for tag_x, untranslated_filter in zip("ZYXWVUTSRQPON", request.get("filter", ())):
            for field, value in untranslated_filter.items():
                tag_y, *parser = self.filter_map[field]
                result[tag_x + tag_y] = parser[0](value) if parser else value
        return result

    def finalize_response(self, response):
        if "totalItems" not in response:  # Failure
            return response

        response["currentPage"] = self.raw_request.get("page", 1)
        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        response[self.type_name] = parsers.unpivot_dict(response[self.type_name])
        return response


def name_or_uuid(name_tag="KN", uuid_tag="ID"):
    def tag_picker(value, field):
        if is_uuid(value):
            return uuid_tag, hex_to_uuid(value)
        return name_tag, value

    return tag_picker
