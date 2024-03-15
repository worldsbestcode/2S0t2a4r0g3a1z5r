"""
@file      kmes/schemas/keys.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /api/keys endpoint
"""

from marshmallow import Schema, fields, pre_load
from marshmallow.validate import Length, OneOf, Range

import lib.utils.hapi_excrypt_map as ExcryptMap
from lib.utils.string_utils import string_is_hex

from .shared_schemas import (
    Attributes,
    Enum,
    SecurityUsage,
    StringEnum,
    UniqueId,
    ValidityPeriod,
    require_exactly_one,
)


class CreateRandomKey(Schema):
    groupId = UniqueId()
    group = fields.String()
    name = fields.String(required=True)
    type = Enum(ExcryptMap.DeviceKeyType, required=True)
    majorKey = StringEnum(ExcryptMap.MajorKeys, missing="PMK")
    algorithm = fields.String(required=True, validate=OneOf(ExcryptMap.KeyAlgorithms.keys()))
    keyUsage = fields.String(required=True, validate=OneOf(ExcryptMap.KeyUsage.Symmetric.keys()))
    securityUsage = SecurityUsage(anon_sign=False)
    validityPeriod = fields.Nested(ValidityPeriod)
    owner = fields.String()
    mailAddress = fields.String()
    attributes = fields.List(fields.Nested(Attributes))
    ksn = fields.String()
    ksnIncrement = fields.Integer(validate=Range(1))
    tr31Header = fields.String()
    # hsmStorage is vaildated in the Router first
    hsmStorage = fields.String(required=True, validate=OneOf(["trusted", "protected"]))

    validate_ids = require_exactly_one("groupId", "group")

    @pre_load
    def check_legacy(self, data, **kwargs):
        legacy_conversions = {
            "Derivation key": "GenericBdk",
            "Data encryption key": "DataEncryption",
            "Message authentication key (MAC key)": "MacKey",
            "Key encryption key": "HsmProtectedKeyTransfer",
        }
        if data.get("type", None) in legacy_conversions:
            data["type"] = legacy_conversions[data["type"]]
        return data


class CreateRandomProtectedKey(Schema):
    groupId = fields.String()
    group = fields.String()
    name = fields.String(required=True)
    owner = fields.String()
    mailAddress = fields.String()
    validityPeriod = fields.Nested(ValidityPeriod)
    hsmStorage = fields.String(required=True, validate=OneOf(["trusted", "protected"]))

    validate_ids = require_exactly_one("groupId", "group")


class ExportSymmetricKey(Schema):
    export_format = set(ExcryptMap.CryptogramExportType.keys())
    export_format.remove("Clear")

    name = fields.String()
    id = UniqueId()
    group = fields.String()
    groupId = UniqueId()
    hostname = fields.String()
    transferKey = fields.String()
    format = fields.String(validate=OneOf(export_format), missing="Cryptogram")
    akbHeader = fields.String()
    useCbc = fields.Boolean(missing=False)
    checksumLength = fields.Integer(validate=OneOf([4, 5, 6]))
    # hsmStorage is vaildated in the Router first
    hsmStorage = fields.String(required=True, validate=OneOf(["trusted", "protected"]))

    validate_ids = require_exactly_one("name", "id", "group", "groupId")


class ExportSymmetricProtectedKey(Schema):
    id = UniqueId()
    name = fields.String()
    transferKey = fields.String()
    transferKeyGroup = fields.String()
    format = fields.String(validate=OneOf(ExcryptMap.ProtectedKeyExportType.keys()), required=True)
    randomPassphrase = fields.Boolean(missing=False)
    passphrase = fields.String(validate=[string_is_hex, Length(min=2)])
    hsmStorage = fields.String(required=True, validate=OneOf(["trusted", "protected"]))

    validate_ids = require_exactly_one("id", "name")


class RetrieveSymmetricProtectedKeyGroup(Schema):
    groupId = UniqueId()
    group = fields.String()
    format = fields.String(validate=OneOf(ExcryptMap.ProtectedKeyRetrieveType.keys()))
    randomPassphrase = fields.Boolean(missing=False)
    passphrase = fields.String(validate=[string_is_hex, Length(min=2)])
    hsmStorage = fields.String(required=True, validate=OneOf(["trusted", "protected"]))

    validate_ids = require_exactly_one("groupId", "group")


class DeleteTrustedKey(Schema):
    id = UniqueId()
    name = fields.String()
    validate_ids = require_exactly_one("name", "id")

    # hsmStorage is vaildated in the Router first
    hsmStorage = fields.String(required=True, validate=OneOf(["trusted", "protected"]))


class DeleteProtectedKey(DeleteTrustedKey):
    _operation = fields.Constant("delete")


class ImportKey(Schema):
    algorithm = fields.String(required=True, validate=OneOf(ExcryptMap.KeyAlgorithms))
    attributes = fields.List(fields.Nested(Attributes))
    checksum = fields.String(required=True, validate=string_is_hex)
    checksumAlgorithm = fields.String(validate=OneOf({"CMAC", "Financial"}), missing="Financial")
    securityUsage = SecurityUsage(anon_sign=False)
    keyBlock = fields.String(required=True)
    group = fields.String()
    groupId = UniqueId()
    name = fields.String(required=True)
    type = Enum(ExcryptMap.DeviceKeyType, required=True)
    keyUsage = fields.String(required=True, validate=OneOf(ExcryptMap.KeyUsage.Symmetric.keys()))
    mailAddress = fields.String()
    majorKey = StringEnum(ExcryptMap.MajorKeys, missing="PMK")
    modifier = fields.String(validate=(string_is_hex, Length(1, 2)))
    owner = fields.String()
    tr31Header = fields.String()
    validityPeriod = fields.Nested(ValidityPeriod)

    validate_ids = require_exactly_one("groupId", "group")
