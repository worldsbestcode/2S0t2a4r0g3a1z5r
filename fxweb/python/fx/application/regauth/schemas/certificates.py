"""
@file      regauth/schemas/certificates.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /api/certificates endpoint
"""

from marshmallow import Schema, fields, validates_schema
from marshmallow import ValidationError
from marshmallow.validate import Length, OneOf, Range

import lib.utils.hapi_excrypt_map as ExcryptMap
from lib.utils.string_utils import string_is_hex
from .shared_schemas import require_exactly_one

__all__ = [
    'ECCVerify',
    'ECIESDecrypt',
    'ECIESEncrypt',
    'ExportCertificate',
    'ImportPkcs12Certificate',
    'GenerateSignature',
    'ListCertificates',
    'RetrievePKIRequest',
    'RSAEncryptDecrypt',
    'RSAVerify',
]


# TODO MERGE use the KeyOptions that already exists in kmes schemas
class KeyOptions(Schema):
    majorKey = fields.String(validate=OneOf(ExcryptMap.MajorKeys.keys()))
    keyUsage = fields.String(validate=OneOf(ExcryptMap.KeyUsageMulti.keys()))


def pki_cert_validator(data):
    pkiTree = data.get('pkiTree', None)
    certId = data.get('certId', None)
    certCommonName = data.get('certCommonName', None)
    certAlias = data.get('certAlias', None)

    error_flag = False
    error_message = ''
    field_list = []

    if pkiTree is not None:
        field_list.append('certCommonName, certAlias')
        if certCommonName is None and certAlias is None:
            error_message = 'One field must be specified if pkiTree is specified'
            error_flag = True

        elif certCommonName and certAlias:
            error_message = 'Only one field must be specified if pkiTree is specified'
            error_flag = True

    elif pkiTree is None and certId is None:
        field_list.append('pkiTree, certId')
        error_message = 'Must specify pkiTree or certId'
        error_flag = True

    if error_flag:
        raise ValidationError(error_message, ', '.join(field_list))


class RetrievePKIRequest(Schema):
    requestType = fields.String(required=True)
    requestId = fields.String(required=True)
    _format = fields.String()

    @validates_schema
    def rebuild_error_response(self, data, **kwargs):
        if data["_format"] not in ["DER", "PEM"]:
            raise ValidationError("Not a valid choice", "format")        

class ExportCertificate(Schema):
    pkiTree = fields.String(required=True)
    certCommonName = fields.String()
    certAlias = fields.String()
    filename = fields.String()
    _format = fields.String()    


    _validate_requested_cert = require_exactly_one('certCommonName', 'certAlias')
    @validates_schema
    def rebuild_error_response(self, data, **kwargs):
        if data["_format"] not in ["DER", "PEM", "JSON"]:
            raise ValidationError("Not a valid choice", "format")        


class ImportPkcs12Certificate(Schema):
    data = fields.String(required=True)
    pkiTree = fields.String(required=True)
    parent = fields.String()
    parentAlias = fields.String()
    passphrase = fields.String()
    passphrasePkcs8 = fields.String()
    type = fields.String()

    keyOptions = fields.Nested(KeyOptions)


class ListCertificates(Schema):
    requestType = fields.String()
    pkiTree = fields.String(required=True)
    parent = fields.String()
    page = fields.Integer(validate=Range(min=1), missing=1)
    pageCount = fields.Integer(validate=Range(min=1, max=250), missing=50)


class RSAEncryptDecrypt(Schema):
    pkiTree = fields.String()
    certId = fields.String()
    certCommonName = fields.String()
    certAlias = fields.String()
    hashType = fields.String(
        validate=OneOf(ExcryptMap.RSAHashTypes.keys()),
        missing='SHA-256'
    )
    data = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )

    @validates_schema
    def validate_pki_cert_selection(self, data, **kwargs):
        pki_cert_validator(data)


class GenerateSignature(Schema):
    pkiTree = fields.String()
    certId = fields.String()
    certCommonName = fields.String()
    certAlias = fields.String()
    dataIsHashed = fields.Boolean(required=True)
    hashType = fields.String(
        required=True,
        validate=OneOf(ExcryptMap.HashTypes.keys())
    )
    padding = fields.String(
        validate=OneOf(ExcryptMap.PaddingMode.keys()),
        missing='PKCS #1'
    )
    data = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )

    @validates_schema
    def validate_pki_cert_selection(self, data, **kwargs):
        pki_cert_validator(data)


class RSAVerify(Schema):
    pkiTree = fields.String()
    certId = fields.String()
    certCommonName = fields.String()
    certAlias = fields.String()
    dataIsHashed = fields.Boolean(required=True)
    hashType = fields.String(
        required=True,
        validate=OneOf(ExcryptMap.RSAVerifyHashTypes.keys())
    )
    padding = fields.String(
        validate=OneOf(ExcryptMap.RSAVerifyPadding.keys()),
        missing='PKCS #1'
    )
    saltLength = fields.Integer()
    data = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )
    signature = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )

    @validates_schema
    def validate_pki_cert_selection(self, data, **kwargs):
        pki_cert_validator(data)


class ECIESEncrypt(Schema):
    pkiTree = fields.String()
    certId = fields.String()
    certCommonName = fields.String()
    certAlias = fields.String()
    derivedKeyHashType = fields.String(
        validate=OneOf(ExcryptMap.ECIESHashTypes.keys()),
        missing='SHA-256'
    )
    iterationCount = fields.Integer(
        validate=Range(min=1, max=4294967295),
        missing=1
    )
    data = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )
    sharedInfo = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )

    @validates_schema
    def validate_pki_cert_selection(self, data, **kwargs):
        pki_cert_validator(data)


class ECIESDecrypt(Schema):
    pkiTree = fields.String()
    certId = fields.String()
    certCommonName = fields.String()
    certAlias = fields.String()
    derivedKeyHashType = fields.String(
        validate=OneOf(ExcryptMap.ECIESHashTypes.keys()),
        missing='SHA-256'
    )
    iterationCount = fields.Integer(
        validate=Range(min=1, max=4294967295),
        missing=1
    )
    data = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )
    sharedInfo = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )
    ephemeralPublicKey = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )

    @validates_schema
    def validate_pki_cert_selection(self, data, **kwargs):
        pki_cert_validator(data)


class ECCVerify(Schema):
    ecc_hash_types = set(ExcryptMap.ECIESHashTypes.keys())
    ecc_hash_types.remove('None')

    pkiTree = fields.String()
    certId = fields.String()
    certCommonName = fields.String()
    certAlias = fields.String()
    dataIsHashed = fields.Boolean(required=True)
    hashType = fields.String(
        validate=OneOf(ecc_hash_types),
        missing='SHA-256'
    )
    data = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )
    signature = fields.String(
        required=True,
        validate=[string_is_hex, Length(min=2)]
    )

    @validates_schema
    def validate_pki_cert_select(self, data, **kwargs):
        pki_cert_validator(data)
