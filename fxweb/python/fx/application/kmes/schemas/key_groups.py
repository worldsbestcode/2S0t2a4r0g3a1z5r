"""
@file      kmes/schemas/key_groups.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /api/key-groups endpoint
"""

from marshmallow import Schema, fields
from marshmallow.validate import ContainsOnly, Length

from .shared_schemas import PaginationMixin, PermissionsMap, require_exactly_one

NAME_VALIDATOR = (  # from StringUtils::isValidKeyGroupName
    Length(1, 30),
    ContainsOnly("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._ -"),
)


class ListKeyGroups(PaginationMixin, Schema):
    parentId = fields.String()


class RetrieveKeyGroup(Schema):
    id = fields.String(required=True)


class MoveKeyGroup(Schema):
    id = fields.String(required=True, validate=Length(1))
    parentId = fields.String(required=True, validate=Length(1), allow_none=True)


class CreateKeyFolder(Schema):
    name = fields.String(required=True, validate=NAME_VALIDATOR)
    parentId = fields.String(validate=NAME_VALIDATOR)
    owner = fields.String()
    mailAddress = fields.String()
    permissions = PermissionsMap()


class UpdateKeyFolder(Schema):
    id = fields.String(required=True)
    newName = fields.String(validate=NAME_VALIDATOR)
    owner = fields.String()
    mailAddress = fields.String()
    permissions = PermissionsMap()


class DeleteKeyFolder(Schema):
    id = fields.String(required=True)


class RotateKeyStore(Schema):
    id = fields.String(required=True)


class RetrieveKeyGroupPermissions(Schema):
    id = fields.String()
    name = fields.String()
    _validate_exactly_one = require_exactly_one("id", "name")


class UpdateKeyGroupPermissions(Schema):
    id = fields.String()
    name = fields.String()
    permissions = PermissionsMap()
