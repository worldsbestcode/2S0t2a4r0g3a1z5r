"""
@file      kmes/translators/user_groups.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators defined for the User Groups method view
"""
from base.base_translator import BaseTranslator, MultiCommandTranslator
from kmes import kmes_parsers
from kmes.schemas import user_groups as schemas
from lib.utils import hapi_parsers as parsers


class CreateUserGroup(BaseTranslator):
    """
    Create a user group
    """

    request_schema = schemas.CreateUserGroup()

    def __init__(self, server_interface):
        request_map = {
            "name": "NA",
            "parentGroup": "PA",
            "loginsRequired": "NU",
            "ldapVerify": ("LV", parsers.serialize_bool),
            "permissions": ("PM", kmes_parsers.serialize_permissions),
            "passPolicy": ("PP", kmes_parsers.serialize_password_policy),
            "userLocation": "SL",
            "ldapGroup": "LG",
            "otpSettings.required": ("OR", parsers.serialize_bool),
            "otpSettings.portList": ("OP", parsers.serialize_csv),
            "otpSettings.timeout": "OO",
            "oauthSettings.hostName": "HO",
            "oauthSettings.tokenLifetime": "TO",
            "oauthSettings.clientId": "KI",
            # TODO(@dneathery): update when "OAuth Enabled" added to RKCW
            # 'oauthSettings.enabled': 'OA'
            # TODO(@dneathery): update when "OAuth MAC key name" added to RKCW
            # 'oauthSettings.macKeyName': 'OK'
        }
        response_map = {"AN": "status", "BB": "message"}
        super().__init__(server_interface, "User", "RKCW", request_map, response_map)


class ListUserGroups(BaseTranslator):
    """
    Retrieves pages of all permissible user groups with basic attributes
    """

    request_schema = schemas.ListUserGroups()

    def __init__(self, server_interface):
        request_map = {
            "page": ("CH", lambda s: int(s) - 1),  # chunks start at 0, pages start at 1
            "pageCount": "CO",
            "parentGroup": "PG",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": ("userGroups.id", parsers.parse_csv),
            "NA": ("userGroups.name", parsers.parse_csv),
            "LR": ("userGroups.loginsRequired", parsers.parse_csv_int),
            "DF": ("userGroups.otpEnabled", parsers.parse_csv_bool),
            "CR": ("userGroups.lastModified", parsers.parse_csv),
            "UC": ("userGroups.numUsers", parsers.parse_csv_int),
            "LD": ("userGroups.ldapVerify", parsers.parse_csv_bool),
            "TO": ("totalItems", int),
            "CT": ("totalPages", int),
        }
        super().__init__(server_interface, "User", "PGUG", request_map, response_map)

    def finalize_response(self, response):
        response.setdefault("status", "Y")  # PGUG no status == success
        response.setdefault("message", "")
        if response["status"] != "Y" or "totalItems" not in response:
            return response

        response["currentPage"] = self.raw_request.get("page", 1)
        response["pageCount"] = self.raw_request.get("pageCount", 50)
        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        # Transpose/unpivot userGroups from dict of lists to list of dicts:
        response["userGroups"] = parsers.unpivot_dict(response["userGroups"])

        # Group is inactive when it has insufficient users for login:
        for group in response["userGroups"]:
            group["active"] = group["numUsers"] >= group["loginsRequired"]

        return response


class RetrieveUserGroup(MultiCommandTranslator):
    """
    Retrieves the permissions and info of the named user group
    """

    request_schema = schemas.RetrieveUserGroup()

    def __init__(self, server_interface):
        request_map = {
            # RKRP:
            "group": "NA",
            # RKPS:
            "map_type": "FN",
        }
        response_map = {
            "AN": ("status"),
            "BB": ("message"),
            # RKRP:
            "PM": ("permissions", kmes_parsers.parse_permission_map),
            "PP": ("passPolicy", kmes_parsers.parse_password_policy),
            "NU": ("loginsRequired", int),
            "OA": ("oauthSettings.enabled", parsers.parse_bool),
            "LT": ("oauthSettings.tokenLifetime", int),
            "CI": ("oauthSettings.clientId"),
            "OK": ("oauthSettings.hostName"),
            "OT": ("otpSettings.required", parsers.parse_bool),
            "OP": ("otpSettings.portList", parsers.parse_csv),
            "OO": ("otpSettings.timeout"),
            "SL": ("userLocation"),
            "LV": ("ldapVerify", parsers.parse_bool),
            "LG": ("ldapGroup"),
            # RKPS:
            "TY": ("names", parsers.parse_csv),
            "DS": ("descriptions", parsers.parse_csv),
        }
        super().__init__(
            server_interface, ("Misc", "User"), ("RKPS", "RKRP"), request_map, response_map
        )

    def preprocess_request(self, request):
        request["map_type"] = "types"  # ensure we get the permission descriptions for perm types
        return request

    def finalize_response(self, response):
        type_names = dict(zip(response.pop("names", []), response.pop("descriptions", [])))
        if "permissions" not in response:
            return response
        perms = response["permissions"]
        response["permissions"] = kmes_parsers.add_names_to_permissions(
            perms, type_names=type_names
        )
        return response


class UpdateUserGroup(BaseTranslator):
    """
    Update a user group
    """

    request_schema = schemas.UpdateUserGroup()

    def __init__(self, server_interface):
        request_map = {
            "group": "NA",
            "newName": "NB",
            "permissions": ("PM", kmes_parsers.serialize_permissions),
            "passPolicy": ("PP", kmes_parsers.serialize_password_policy),
            "loginsRequired": "NU",
            "ldapVerify": ("LV", parsers.serialize_bool),
            "ldapGroup": "LG",
            "storageLocation": "SL",
            "otpSettings.required": ("OT", parsers.serialize_bool),
            "otpSettings.portList": ("OP", parsers.serialize_csv),
            "otpSettings.timeout": "OO",
            "oauthSettings.tokenLifetime": "LT",
            "oauthSettings.clientId": "CI",
            # TODO(@dneathery): update when "OAuth Enabled" added to RKEW
            # 'oauthSettings.enabled': 'OA',
            # TODO(@dneathery): update when "OAuth MAC key" added to RKEW
            # 'oauthSettings.macKeyName': 'OK',
        }
        response_map = {"AN": "status", "BB": "message"}
        super().__init__(server_interface, "User", "RKEW", request_map, response_map)


class DeleteUserGroup(BaseTranslator):
    """
    JSON to Excrypt map for deleting a single user group
    """

    request_schema = schemas.DeleteUserGroup()

    def __init__(self, server_interface):
        request_map = {"group": "NA"}
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "User", "RKDW", request_map, response_map)


class MoveUserGroup(BaseTranslator):
    """
    Set the parent group of given user group.
    """

    request_schema = schemas.MoveUserGroup()

    def __init__(self, server_interface):
        request_map = {
            "group": "NA",
            "destination": "PA",
            "fixConflicts": ("FP", parsers.serialize_bool),
        }
        response_map = {"AN": "status", "BB": "message"}
        super().__init__(server_interface, "User", "RKMW", request_map, response_map)
