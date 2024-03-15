"""
@file      kmes/schemas/user_groups.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to user groups API endpoint
"""

from marshmallow import Schema, ValidationError, fields, validates
from marshmallow.validate import Length, OneOf, Range

import lib.utils.hapi_excrypt_map as ExcryptMap

from .shared_schemas import USERGROUP_NAME_VALIDATOR, ClassPermissionsMap, PaginationMixin


class OauthSettings(Schema):
    clientId = fields.String()
    hostName = fields.String(required=True)
    tokenLifetime = fields.Integer(validate=Range(1), missing=10)


class OtpSettings(Schema):
    portList = fields.List(fields.String(validate=OneOf(("Host API", "Client"))))
    required = fields.Boolean(missing=False)
    timeout = fields.Integer(validate=Range(15, 300), missing=30)

    @validates("timeout")
    def is_valid_timeout(self, timeout, **kwargs):
        if timeout % 15 != 0:
            raise ValidationError("Must be multiple of 15 minutes.")


class PasswordPolicy(Schema):
    _policy_field = lambda: fields.Mapping(
        keys=fields.String(validate=OneOf({"min", "max"})),
        values=fields.Integer(validate=Range(0)),
        validate=Length(1),  # Disallow empty dict
    )
    alphabetical = _policy_field()
    length = _policy_field()
    lowercase = _policy_field()
    numeric = _policy_field()
    symbols = _policy_field()
    uppercase = _policy_field()


class CreateUserGroup(Schema):
    ldapGroup = fields.String(validate=USERGROUP_NAME_VALIDATOR)
    ldapVerify = fields.Boolean()
    loginsRequired = fields.Integer(validate=Range(1, 10), missing=2)
    name = fields.String(required=True, validate=USERGROUP_NAME_VALIDATOR)
    oauthSettings = fields.Nested(OauthSettings)
    otpSettings = fields.Nested(OtpSettings)
    parentGroup = fields.String(required=True, validate=USERGROUP_NAME_VALIDATOR)
    passPolicy = fields.Nested(PasswordPolicy)
    permissions = ClassPermissionsMap()
    userLocation = fields.String(validate=OneOf(ExcryptMap.UserGroupStorageLocation.names))


class ListUserGroups(PaginationMixin, Schema):
    parentGroup = fields.String(validate=USERGROUP_NAME_VALIDATOR)


class RetrieveUserGroup(Schema):
    group = fields.String(validate=USERGROUP_NAME_VALIDATOR)


class UpdateUserGroup(Schema):
    ldapGroup = fields.String(validate=USERGROUP_NAME_VALIDATOR)
    ldapVerify = fields.Boolean()
    loginsRequired = fields.Integer(validate=Range(1, 10))
    group = fields.String(required=True, validate=USERGROUP_NAME_VALIDATOR)
    newName = fields.String(validate=USERGROUP_NAME_VALIDATOR)
    oauthSettings = fields.Nested(OauthSettings)
    otpSettings = fields.Nested(OtpSettings)
    passPolicy = fields.Nested(PasswordPolicy)
    permissions = ClassPermissionsMap()
    userLocation = fields.String(validate=OneOf(ExcryptMap.UserGroupStorageLocation.names))


class DeleteUserGroup(Schema):
    group = fields.String(required=True, validate=USERGROUP_NAME_VALIDATOR)


class MoveUserGroup(Schema):
    group = fields.String(required=True, validate=USERGROUP_NAME_VALIDATOR)
    destination = fields.String(required=True, validate=USERGROUP_NAME_VALIDATOR)
    fixConflicts = fields.Boolean(missing=False)
