"""
@file      kmes/translators/approval_groups.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for Signing Approval Group views
"""

from base.base_translator import BaseTranslator
from kmes import kmes_parsers
from kmes.schemas import approval_groups as schemas

from .shared import ObjectLookupTranslator


class CreateApprovalGroup(BaseTranslator):
    """
    JSON to Excrypt map for creating a Signing Approval Group
    """

    request_schema = schemas.CreateApprovalGroup()

    def __init__(self, server_interface):
        request_map = {
            "name": "NA",
        }
        response_map = {"AN": "status", "BB": "message", "ID": "id"}
        super().__init__(server_interface, "ApprovalGroups", "RAAG", request_map, response_map)


class ListApprovalGroups(ObjectLookupTranslator):
    """
    JSON to Excrypt map for listing Signing Approval Groups
    """

    type_enum = "APPROVAL_GROUP"
    type_name = "approvalGroups"
    parent_name = None
    container_name = None


class RetrieveApprovalGroup(BaseTranslator):
    """
    JSON to Excrypt map for retrieving a single Signing Approval Group
    """

    request_schema = schemas.RetrieveApprovalGroup()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
            "NA": "name",
        }
        super().__init__(server_interface, "ApprovalGroups", "RARG", request_map, response_map)


class UpdateApprovalGroup(BaseTranslator):
    """
    JSON to Excrypt map for updating a Signing Approval Group
    """

    request_schema = schemas.UpdateApprovalGroup()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
            "newName": "NB",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "ApprovalGroups", "RAEG", request_map, response_map)


class DeleteApprovalGroup(BaseTranslator):
    """
    JSON to Excrypt map for deleting a Signing Approval Group
    """

    request_schema = schemas.DeleteApprovalGroup()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "name": "NA",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "ApprovalGroups", "RADG", request_map, response_map)


class RetrieveApprovalGroupPermissions(BaseTranslator):
    """
    JSON to Excrypt map for retrieving a single Signing Approval Group Permissions
    """

    request_schema = schemas.RetrieveApprovalGroupPermissions()

    def __init__(self, server_interface):
        fixed_values = {
            "MN": "APPROVAL_GROUP",
        }
        request_map = {
            "id": "ID",
            "name": "NA",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
            "NA": "name",
            "PL": ("permissions", kmes_parsers.parse_mo_permissions,),
        }
        super().__init__(
            server_interface,
            "ApprovalGroups",
            "RKPD",
            request_map,
            response_map,
            fixed_values=fixed_values,
        )


class UpdateApprovalGroupPermissions(BaseTranslator):
    """
    JSON to Excrypt map for retrieving a single Signing Approval Group Permissions
    """

    request_schema = schemas.UpdateApprovalGroupPermissions()

    def __init__(self, server_interface):
        fixed_values = {
            "MN": "APPROVAL_GROUP",
        }

        request_map = {
            "id": "ID",
            "name": "NA",
            "permissions": ("PL", kmes_parsers.serialize_mo_permissions,),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(
            server_interface,
            "ApprovalGroups",
            "RKPM",
            request_map,
            response_map,
            fixed_values=fixed_values,
        )
