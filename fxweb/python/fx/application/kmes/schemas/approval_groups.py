"""
@file      kmes/schemas/approval_groups.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas for Signing Approval Groups
"""

from marshmallow import Schema, fields
from marshmallow.validate import Length

from .shared_schemas import PermissionsMap, UniqueId, require_exactly_one


class CreateApprovalGroup(Schema):
    name = fields.String(required=True, validate=Length(1, 64))


class RetrieveApprovalGroup(Schema):
    id = UniqueId()
    name = fields.String(validate=Length(1, 64))
    _validate_exactly_one = require_exactly_one("id", "name")


class UpdateApprovalGroup(Schema):
    id = UniqueId()
    name = fields.String(validate=Length(1, 64))
    newName = fields.String(validate=Length(1, 64))
    _validate_exactly_one = require_exactly_one("id", "name")


class DeleteApprovalGroup(Schema):
    id = UniqueId()
    name = fields.String(validate=Length(1, 64))
    _validate_exactly_one = require_exactly_one("id", "name")


class RetrieveApprovalGroupPermissions(Schema):
    id = UniqueId()
    name = fields.String(validate=Length(1, 64))
    _validate_exactly_one = require_exactly_one("id", "name")


class UpdateApprovalGroupPermissions(Schema):
    id = UniqueId()
    name = fields.String(validate=Length(1, 64))
    _validate_exactly_one = require_exactly_one("id", "name")
    permissions = PermissionsMap()
