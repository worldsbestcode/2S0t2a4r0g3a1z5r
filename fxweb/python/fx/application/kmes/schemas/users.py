"""
@file      kmes/schemas/users.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to users API endpoint
"""

from marshmallow import Schema, fields
from marshmallow.validate import ContainsOnly, Length, OneOf, Range

import lib.utils.hapi_excrypt_map as ExcryptMap
from lib.utils.string_utils import string_is_b64

_name_validator = (
    Length(4, 64),
    ContainsOnly("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._@-"),
)


class CreateUser(Schema):
    username = fields.String(required=True, validate=_name_validator)
    primaryGroup = fields.String(required=True, validate=_name_validator)
    newPassword = fields.String(required=True, validate=string_is_b64)
    commonName = fields.String(validate=Length(0, 64))
    email = fields.String(validate=Length(0, 64))
    firstName = fields.String(validate=Length(0, 64))
    lastName = fields.String(validate=Length(0, 64))
    mobileCarrier = fields.String(validate=OneOf(ExcryptMap.MobileCarriers))
    phone = fields.String(validate=Length(0, 16))


class ListUsers(Schema):
    page = fields.Integer(validate=Range(1), missing=1)
    pageCount = fields.Integer(validate=Range(1), missing=50)
    usergroup = fields.String(validate=_name_validator)


class RetrieveUser(Schema):
    username = fields.String(required=True, validate=_name_validator)


class UpdateUser(Schema):
    username = fields.String(required=True, validate=_name_validator)
    commonName = fields.String(validate=Length(0, 64))
    email = fields.String(validate=Length(0, 64))
    firstName = fields.String(validate=Length(0, 64))
    lastName = fields.String(validate=Length(0, 64))
    mobileCarrier = fields.String(validate=OneOf(ExcryptMap.MobileCarriers))
    phone = fields.String(validate=Length(0, 16))


class DeleteUser(Schema):
    username = fields.String(required=True, validate=_name_validator)


class MoveUser(Schema):
    username = fields.String(required=True, validate=_name_validator)
    newGroup = fields.String(required=True, validate=_name_validator)
    newPassword = fields.String(validate=string_is_b64)
    oldPassword = fields.String(validate=string_is_b64)


class SetUserPassword(Schema):
    username = fields.String(required=True, validate=_name_validator)
    newPassword = fields.String(required=True, validate=string_is_b64)
    oldPassword = fields.String(validate=string_is_b64)
