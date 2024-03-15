"""
@file      kmes/translators/pki_trees.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for KMES PKI Tree views
"""

from functools import partial

import kmes.schemas.pki_trees as PKITreeSchemas
import lib.utils.hapi_excrypt_map as ExcryptMap
import lib.utils.hapi_parsers as parsers
from base.base_translator import BaseTranslator
from kmes import kmes_parsers


class CreatePKITree(BaseTranslator):
    """
    JSON to Excrypt map for creating a single PKI Tree
    """

    request_schema = PKITreeSchemas.CreatePKITree()

    def __init__(self, server_interface):
        request_map = {
            "name": "NA",
            "pkiType": ("CT", ExcryptMap.PkiCertType.to_int),
            "apiCredential": "CC",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
        }

        super().__init__(server_interface, "PKITrees", "RKCY", request_map, response_map)


class ListPKITrees(BaseTranslator):
    """
    JSON to Excrypt map to retrieve a list PKI Trees
    """

    request_schema = PKITreeSchemas.ListPKITrees()

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "list",
        }
        request_map = {
            "pageCount": "CS",
            "page": ("CH", lambda page: page - 1),
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": ("pkiTrees.id", parsers.parse_csv),
            "NA": ("pkiTrees.name", parsers.parse_csv_hex),
            "CL": ("pkiTrees.empty", partial(parsers.parse_csv_bool, negate=True)),
            "CC": ("totalPages", int),
            "TO": ("totalItems", int),
        }

        super().__init__(
            server_interface, "PKITrees", "TREE", request_map, response_map, fixed_values
        )

    def finalize_response(self, response):
        if not response.success:
            return response

        response.setdefault("totalItems", 0)
        response.setdefault("totalPages", 0)

        response["pkiTrees"] = parsers.unpivot_dict(response["pkiTrees"])

        response["currentPage"] = self.raw_request["page"]
        response["pageCount"] = self.raw_request["pageCount"]

        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        return response


class RetrievePKITree(BaseTranslator):
    """
    JSON to Excrypt map to retrieve a single PKI Tree
    """

    request_schema = PKITreeSchemas.RetrievePKITree()

    def __init__(self, server_interface):
        # NOTE: should provide name or id
        request_map = {
            "name": "NA",
            "id": "ID",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
            "NA": "name",
            "CT": ("pkiType", ExcryptMap.PkiCertType.from_typeToStr),
            "CC": "apiCredential",
            "RT": "rootCert.name",
            "PI": "rootCert.id",
            "FS": ("rootCert.majorKey", ExcryptMap.FWMajorKeySlot.value_to_name),
        }

        super().__init__(server_interface, "PKITrees", "RKGY", request_map, response_map)


class UpdatePKITree(BaseTranslator):
    """
    JSON to Excrypt map to update a single PKI Tree
    """

    request_schema = PKITreeSchemas.UpdatePKITree()

    def __init__(self, server_interface):
        request_map = {
            "name": "NA",
            "id": "ID",
            "newName": "NB",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "PKITrees", "RKMY", request_map, response_map)


class DeletePKITree(BaseTranslator):
    """
    JSON to Excrypt map for deleteing a single PKI Tree
    """

    request_schema = PKITreeSchemas.DeletePKITree()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "PKITrees", "RKDY", request_map, response_map)


class RetrievePKITreePermissions(BaseTranslator):
    """
    JSON to Excrypt map for viewing the permissions of a single PKI tree
    """

    request_schema = PKITreeSchemas.RetrievePKITreePermissions()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "_type": ("MN", "CERTAUTHORITY"),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "ID": "id",
            "PL": ("permissions", kmes_parsers.parse_mo_permissions),
        }

        super().__init__(server_interface, "Misc", "RKPD", request_map, response_map)


class UpdatePKITreePermissions(BaseTranslator):
    """
    JSON to Excrypt map for setting the permissions of a single PKI tree
    """

    request_schema = PKITreeSchemas.UpdatePKITreePermissions()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "_type": ("MN", "CERTAUTHORITY"),
            "permissions": ("PL", kmes_parsers.serialize_mo_permissions),
            "updateChildren": ("RE", ExcryptMap.PermissionScope.name_to_value),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "ID": "id",
        }

        super().__init__(server_interface, "Misc", "RKPM", request_map, response_map)
