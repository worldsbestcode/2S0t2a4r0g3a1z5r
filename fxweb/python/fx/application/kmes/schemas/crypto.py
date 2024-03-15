"""
@file      kmes/schemas/crypto.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Schema validation for crypto operations
"""

from marshmallow import Schema, fields, validates_schema
from marshmallow.validate import Length, OneOf, Range

import lib.utils.hapi_excrypt_map as ExcryptMap
from lib.utils.string_utils import string_is_hex

from .shared_schemas import UniqueId, require_at_least_one, require_exactly_one, require_implication


class SymmetricEncrypt(Schema):
    keyGroup = fields.String()
    keyGroupId = UniqueId()
    key = fields.String()
    keyId = UniqueId()
    padding = fields.Boolean(missing=False)
    cipher = fields.String(validate=OneOf(ExcryptMap.Cipher.keys()), missing="ECB")
    data = fields.String(required=True, validate=string_is_hex)
    dataFormat = fields.String(validate=OneOf(ExcryptMap.DataFormat.keys()), missing="raw")

    validate_ids = require_at_least_one("key", "keyId", "keyGroupId", "keyGroup")


class SymmetricDecrypt(Schema):
    keyGroup = fields.String()
    keyGroupId = UniqueId()
    key = fields.String()
    keyId = UniqueId()
    padding = fields.Boolean()
    cipher = fields.String(validate=OneOf(ExcryptMap.Cipher.keys()))
    data = fields.String(required=True, validate=string_is_hex)
    dataFormat = fields.String(validate=OneOf(ExcryptMap.DataFormat.keys()), missing="raw")

    @validates_schema
    def check_required(self, data, **kwargs):
        if data.get("dataFormat") == "DPM":
            return  # get from header

        data.setdefault("padding", False)
        data.setdefault("cipher", "ECB")
        require_exactly_one("key", "keyId", "keyGroupId", "keyGroup")(self, data)


# Base class for all asymmetric schemas
class BaseAsymmetric(Schema):
    key = fields.String()
    keyId = UniqueId()
    hsmStorage = fields.String(validate=OneOf(["trusted", "stored"]))
    pkiTree = fields.String()
    certId = fields.String()
    certName = fields.String()
    certAlias = fields.String()
    data = fields.String(required=True, validate=[string_is_hex, Length(min=2)])

    _key_identifiers = require_exactly_one("pkiTree", "certId", "key", "keyId")
    _tree_needs_identifier = require_implication("pkiTree", "certName", "certAlias")


class EccEncrypt(BaseAsymmetric):
    derivedKeyHashType = fields.String(
        validate=OneOf(ExcryptMap.ECIESHashTypes.keys()), missing="SHA-256"
    )
    iterationCount = fields.Integer(validate=Range(min=1, max=4294967295), missing=1)
    sharedInfo = fields.String(required=True, validate=[string_is_hex, Length(min=2)])


# Inherits from ECCEncrypt as they share all but one additional field.
class EccDecrypt(EccEncrypt):
    ephemeralPublicKey = fields.String(required=True, validate=[string_is_hex, Length(min=2)])


class RsaEncryptDecrypt(BaseAsymmetric):
    hashType = fields.String(validate=OneOf(ExcryptMap.RSAHashTypes.keys()), missing="SHA-256")


class EccSign(BaseAsymmetric):
    dataIsHashed = fields.Boolean(required=True)
    hashType = fields.String(required=True, validate=OneOf(ExcryptMap.HashTypes.keys()))


class RsaSign(BaseAsymmetric):
    dataIsHashed = fields.Boolean(required=True)
    hashType = fields.String(required=True, validate=OneOf(ExcryptMap.HashTypes.keys()))
    padding = fields.String(validate=OneOf(ExcryptMap.PaddingMode.keys()), missing="PKCS #1")
    saltLength = fields.Integer()


class EccVerify(BaseAsymmetric):
    ecc_hash_types = set(ExcryptMap.ECIESHashTypes.keys())
    ecc_hash_types.remove("None")

    dataIsHashed = fields.Boolean(required=True)
    hashType = fields.String(validate=OneOf(ecc_hash_types), missing="SHA-256")
    signature = fields.String(required=True, validate=[string_is_hex, Length(min=2)])


# Inherits from ECCVerify due to two matching fields. hashType validates differently though.
class RsaVerify(EccVerify):
    hashType = fields.String(required=True, validate=OneOf(ExcryptMap.RSAVerifyHashTypes.keys()))
    padding = fields.String(validate=OneOf(ExcryptMap.RSAVerifyPadding.keys()), missing="PKCS #1")
    saltLength = fields.Integer()


class Random(Schema):
    size = fields.Integer(validate=Range(min=1, max=7680), required=True)
