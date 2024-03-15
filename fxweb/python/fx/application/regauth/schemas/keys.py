"""
@file      regauth/schemas/keys.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /api/keys endpoint
"""

from marshmallow import Schema, fields, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import OneOf, Length

import lib.utils.hapi_excrypt_map as ExcryptMap
from lib.utils.string_utils import string_is_hex
from .shared_schemas import Attributes, ValidityPeriod, require_exactly_one


__all__ = [
    'CreateRandomKey',
    'CreateRandomProtectedKey',
    'ImportProtectedKey',
    'ExportSymmetricKey',
    'ExportSymmetricProtectedKey',
    'RetrieveSymmetricProtectedKeyGroup',
    'GeneralEncryptDecrypt',
]


class CreateRandomKey(Schema):
    export_format = set(ExcryptMap.CryptogramExportType.keys())
    export_format.remove("Clear")

    keyGroupId = fields.String(required=True)
    keyName = fields.String(required=True)
    keyType = fields.String(
        required=True,
        validate=OneOf(ExcryptMap.KeyTypes.keys())
    )
    majorKey = fields.String(validate=OneOf(ExcryptMap.MajorKeys.keys()))
    format = fields.String(
        validate=OneOf(export_format),
        missing='Cryptogram'
    )
    algorithm = fields.String(
        required=True,
        validate=OneOf(ExcryptMap.KeyAlgorithms.keys())
    )
    keyUsage = fields.String(
        required=True,
        validate=OneOf(ExcryptMap.KeyUsage.Symmetric.keys())
    )
    clearExport = fields.Boolean(missing=False)
    validityPeriod = fields.Nested(ValidityPeriod)
    owner = fields.String()
    mailAddress = fields.String()
    attributes = fields.List(
        fields.Nested(Attributes)
    )
    tr31Header = fields.String()
    akbHeader = fields.String()


class CreateRandomProtectedKey(Schema):
    keyGroupId = fields.String()
    keyGroup = fields.String()
    keyName = fields.String(required=True)
    owner = fields.String()
    mailAddress = fields.String()

    validate_ids = require_exactly_one("keyGroupId", "keyGroup")


class ImportProtectedKey(Schema):
    keyGroupId = fields.String()
    keyGroup = fields.String()
    keyName = fields.String(required=True)
    data = fields.String(required=True)
    format = fields.String(required=True)
    wrappingKey = fields.String()
    wrappingKeyGroup = fields.String()
    passphrase = fields.String()
    operation = fields.String(required=True)
    hsmStorage = fields.String(required=True)

    @validates_schema
    def validate_ids(self, data, **kwargs):
        require_exactly_one("keyGroupId", "keyGroup")


class ExportSymmetricKey(Schema):
    export_format = set(ExcryptMap.CryptogramExportType.keys())
    export_format.remove("Clear")

    keyId = fields.String()
    keyGroupId = fields.String()
    hostname = fields.String()
    transferKey = fields.String()
    format = fields.String(
        validate=OneOf(export_format),
        missing='Cryptogram'
    )
    akbHeader = fields.String()
    useCbc = fields.Boolean(missing=False)
    checksumLength = fields.Integer(validate=OneOf([4, 5, 6]))
    returnKeyGroup = fields.Boolean(missing=False)

    validate_ids = require_exactly_one("keyId", "keyGroupId")


class ExportSymmetricProtectedKey(Schema):
    keyId = fields.String()
    keyName = fields.String()
    transferKey = fields.String()
    format = fields.String(
        validate=OneOf(ExcryptMap.ProtectedKeyExportType.keys()),
        required=True
    )
    randomPassphrase = fields.Boolean(missing=False)
    passphrase = fields.String(
        validate=[string_is_hex, Length(min=2)]
    )

    validate_ids = require_exactly_one("keyId", "keyName")


class RetrieveSymmetricProtectedKeyGroup(Schema):
    keyGroupId = fields.String()
    keyGroup = fields.String()
    format = fields.String(
        validate=OneOf(ExcryptMap.ProtectedKeyRetrieveType.keys())
    )
    randomPassphrase = fields.Boolean(missing=False)
    passphrase = fields.String(
        validate=[string_is_hex, Length(min=2)]
    )

    validate_ids = require_exactly_one("keyGroupId", "keyGroup")


class GeneralEncryptDecrypt(Schema):
    keyGroupId = fields.String()
    keyId = fields.String()
    padding = fields.Boolean(missing=False)
    cipher = fields.String(
        validate=OneOf(ExcryptMap.Cipher.keys()),
        missing='ECB'
    )
    data = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )
    dataFormat = fields.String(
        validate=OneOf(ExcryptMap.DataFormat.keys()),
        missing='raw'
    )
    mode = fields.String(validate=OneOf(['0', '1']))
    continueMode = fields.String(validate=OneOf(['0', '1']))
    continueId = fields.String()
