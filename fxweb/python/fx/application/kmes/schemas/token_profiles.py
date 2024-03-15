"""
@file      kmes/schemas/token_profiles.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION

Request validation schemas related to the token_profiles endpoint
"""

from marshmallow import Schema, ValidationError, fields, validates_schema
from marshmallow.validate import Length, OneOf, Range

from lib.utils.hapi_excrypt_map import DUKPTTypes, FpeAlgorithm

from .shared_schemas import (
    EncodedString,
    Enum,
    Hex,
    NameIdLink,
    PermissionsMap,
    StringEnum,
    UniqueId,
    require_exactly_one,
    require_separate,
    require_together,
)


class CreateTokenProfile(Schema):
    algorithm = Enum(FpeAlgorithm, missing=FpeAlgorithm.FF3_1)
    keyId = UniqueId()
    luhnCheck = fields.Boolean()
    name = fields.String(required=True)
    owner = fields.String()
    paddingLength = fields.Integer(validate=Range(0, 4096))
    prefix = fields.String(validate=Length(0, 32))
    preserveLeading = fields.Integer(validate=Range(0, 4096))
    preserveTrailing = fields.Integer(validate=Range(0, 4096))
    cipher = fields.String(validate=OneOf(["OFB", "CBC", "None"]))
    outputRegex = fields.String()
    inputRegex = fields.String()
    ivMode = fields.String(validate=OneOf(["Disabled", "Chained", "Random"]))
    ivSize = fields.String()
    reversible = fields.Boolean()
    inputValidation = fields.String(validate=OneOf(["Disabled", "Output Regex", "Custom Regex"]))
    namespace = fields.String()

    verificationLength = fields.Integer(validate=Range(0, 4096))
    _validate_separate = require_separate(
        [
            "cipher",
            "outputRegex",
            "inputRegex",
            "ivMode",
            "ivSize",
            "reversible",
            "inputValidation",
        ],
        [
            "prefix",
            "preserveLeading",
            "preserveTrailing",
            "namespace",
            "verificationLength",
            "luhnCheck",
        ],
    )

    @validates_schema
    def check_length(self, data, **kwargs):
        check_attr_length(data)


class RetrieveTokenProfile(Schema):
    id = UniqueId(required=True)


class UpdateTokenProfile(Schema):
    id = UniqueId()
    name = fields.String()
    newName = fields.String()
    keyId = UniqueId()
    keyGroup = fields.String()
    verificationLength = fields.Integer(validate=Range(max=99))
    luhnCheck = fields.Boolean()
    paddingLength = fields.Integer(validate=Range(max=99))
    prefix = fields.String(validate=Length(0, 32))
    preserveLeading = fields.Integer(validate=Range(0, 4096))
    preserveTrailing = fields.Integer(validate=Range(0, 4096))
    namespace = fields.String()
    cipher = fields.String(validate=OneOf(["OFB", "CBC", "None"]))
    outputRegex = fields.String()
    inputRegex = fields.String()
    ivMode = fields.String(validate=OneOf(["Disabled", "Chained", "Random"]))
    ivSize = fields.String()
    reversible = fields.Boolean()
    inputValidation = fields.String(validate=OneOf(["Disabled", "Output Regex", "Custom Regex"]))

    _validate_exactly_one = require_exactly_one("id", "name")
    _validate_separate = require_separate(
        [
            "cipher",
            "outputRegex",
            "inputRegex",
            "ivMode",
            "ivSize",
            "reversible",
            "inputValidation",
        ],
        [
            "prefix",
            "preserveLeading",
            "preserveTrailing",
            "namespace",
            "verificationLength",
            "luhnCheck",
        ],
    )

    @validates_schema
    def check_length(self, data, **kwargs):
        check_attr_length(data)


class DeleteTokenProfile(Schema):
    id = UniqueId(required=True)


class RetrievePermissions(Schema):
    id = UniqueId()
    name = fields.String()
    _validate_exactly_one = require_exactly_one("id", "name")


class UpdatePermissions(Schema):
    id = UniqueId()
    name = fields.String()
    _validate_exactly_one = require_exactly_one("id", "name")
    permissions = PermissionsMap()


def check_attr_length(data):
    padding = data.get("paddingLength", 0)
    leading = data.get("preserveLeading", 0)
    trailing = data.get("preserveTrailing", 0)
    if padding and padding < leading + trailing + 2:
        raise ValidationError(
            field_name="paddingLength",
            message="Must be at least 2 greater than preserved length",
        )


class Tokenize(Schema):
    data = EncodedString(required=True)
    profile = NameIdLink(required=True)
    cardholderProfile = NameIdLink()
    keyGroup = NameIdLink()
    key = NameIdLink()
    ksn = Hex(validate=Length(max=20))
    dukptVariant = StringEnum(DUKPTTypes.keys())
    _validate_require_together = require_together("ksn", "dukptVariant")

    @validates_schema
    def require_group_if_key_is_by_name(self, data, **kwargs):
        key_name_given = "name" in data.get("key", ())
        key_group_given = "keyGroup" in data
        if key_name_given and not key_group_given:
            raise ValidationError("Key group required for key name", "keyGroup")


class Detokenize(Schema):
    token = EncodedString(required=True)
    profile = NameIdLink(required=True)
    cardholderProfile = NameIdLink()
    key = NameIdLink()
    verifyOnly = fields.Boolean()
