"""
@file      kmes/translators/users.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators defined for the Users method view
"""

import functools

from base.base_translator import BaseTranslator, MultiCommandTranslator
from kmes.schemas import users as schemas
from lib.utils import hapi_parsers as parsers
from lib.utils.string_utils import b64_to_hex


class CreateUser(BaseTranslator):
    """
    Create a new user.
    """

    request_schema = schemas.CreateUser()

    def __init__(self, server_interface):
        request_map = {
            "username": "NA",
            "primaryGroup": "PA",
            "newPassword": ("PX", b64_to_hex),
            "commonName": "CA",
            "email": "EM",
            "firstName": "GA",
            "lastName": "SA",
            "mobileCarrier": "TC",
            "phone": "TX",
        }
        response_map = {"AN": "status", "BB": "message"}

        super().__init__(server_interface, "User", "RKCU", request_map, response_map)


class ListUsers(BaseTranslator):
    """
    Retrieves pages of all permissible identities with basic attributes
    """

    request_schema = schemas.ListUsers()

    def __init__(self, server_interface):
        request_map = {
            "page": ("CH", lambda n: int(n) - 1),  # chunks start at 0, pages start at 1
            "pageCount": "CO",
            "usergroup": "GR",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": ("users.id", parsers.parse_csv),
            "DA": ("users.username", parsers.parse_csv),
            "GR": ("users.subGroups", parsers.parse_pipe_list),
            "LL": ("users.lastLogin", parsers.parse_csv),
            "LO": ("users.valid", functools.partial(parsers.parse_csv_bool, negate=True)),
            "TO": ("totalItems", int),
            "CT": ("totalPages", int),
        }

        super().__init__(server_interface, "User", "PGUS", request_map, response_map)

    def finalize_response(self, response):
        if "status" in response:  # was not successful
            return response

        response["currentPage"] = self.raw_request.get("page", 1)
        response["pageCount"] = self.raw_request.get("pageCount", 50)
        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        # Transpose/unpivot users from dict of lists to list of dicts:
        response["users"] = parsers.unpivot_dict(response["users"])

        # The first group is the primary, the rest are sub groups:
        for user in response["users"]:
            user["primaryGroup"] = user["subGroups"].pop(0) if user["subGroups"] else ""

        return response


class RetrieveUser(MultiCommandTranslator):
    """
    JSON to Excrypt map to get the info of a single user.
    """

    request_schema = schemas.RetrieveUser()

    def __init__(self, server_interface):
        request_map = {
            # both PGUS and RKRI:
            "username": "NA",
            # PGUS:
            "page": "CH",  # OFFSET
            "pageSize": "CO",  # LIMIT
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            # RKRI:
            "CN": "commonName",
            "EM": "email",
            "GA": "firstName",
            "SA": "lastName",
            "TC": "mobileCarrier",
            "TX": "phone",
            # PGUS:
            "DA": "username",
            "LO": ("enabled", lambda s: s == "0"),
            "LL": "lastLogin",
            "GR": ("subGroups", parsers.parse_pipe_list),
            # computed 'primaryGroup' from 'subGroups'
            # 'ID': 'uuid',
            # 'DC': 'dateModified',
        }
        command_categories = ("User", "User")
        command_names = ("PGUS", "RKRI")
        super().__init__(
            server_interface, command_categories, command_names, request_map, response_map
        )

    def preprocess_request(self, request):
        # Ensure we only get 1 result:
        request["page"] = 0
        request["pageSize"] = 1
        return request

    def on_receipt(self, response):
        # If the first command fails, do not attempt the second command:
        if response.get("AN", "Y") != "Y" or response.get("BB", ""):
            raise NotImplementedError(response["AN"])  # TODO(@dneathery): KAPI-270
        return response

    def finalize_response(self, response):
        # Add 'primaryGroup' to response, derived from subGroups.
        # Primary's the first group; flatten remainder as there's only 1 user
        if "subGroups" in response:
            response["primaryGroup"], *response["subGroups"] = response["subGroups"].pop()
        return response


class UpdateUser(BaseTranslator):
    """
    Edit the personal information of a user.
    """

    request_schema = schemas.UpdateUser()

    def __init__(self, server_interface):
        request_map = {
            "username": "NA",
            "commonName": "CA",
            "email": "EM",
            "firstName": "GA",
            "lastName": "SA",
            "mobileCarrier": "TC",
            "phone": "TX",
        }
        response_map = {"AN": "status", "BB": "message"}
        super().__init__(server_interface, "User", "RKUU", request_map, response_map)


class DeleteUser(BaseTranslator):
    """
    Delete the specified user.
    """

    request_schema = schemas.DeleteUser()

    def __init__(self, server_interface):
        request_map = {"username": "NA"}
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "User", "RKDU", request_map, response_map)


class MoveUser(BaseTranslator):
    """
    Move a user from one User Group to another.
    """

    request_schema = schemas.MoveUser()

    def __init__(self, server_interface):
        request_map = {
            "username": "NA",
            "newGroup": "PA",
            "oldPassword": ("PX", b64_to_hex),
            "newPassword": ("NX", b64_to_hex),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "User", "RKMU", request_map, response_map)


class SetUserPassword(BaseTranslator):
    """
    Change a user's password, or set a password if logged in group is Admin.
    """

    request_schema = schemas.SetUserPassword()

    def __init__(self, server_interface):
        request_map = {
            "username": "UN",
            "oldPassword": ("PW", b64_to_hex),
            "newPassword": ("PX", b64_to_hex),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }
        super().__init__(server_interface, "User", "RKNP", request_map, response_map)

    def preprocess_request(self, request):
        if "oldPassword" not in request:
            # If administrator is logged in, the password will be set without
            # checking the old password, but the field must still be non-empty.
            request["oldPassword"] = "AA=="  # b64 'AA==' becomes 0x00 aka b'\0'

        return request
