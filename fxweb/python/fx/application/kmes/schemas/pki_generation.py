"""
@file      kmes/schemas/pki_generation.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas for PKI Generation Requests
"""

from marshmallow import Schema, ValidationError, fields, post_load, validates_schema
from marshmallow.fields import Boolean, DateTime, Nested, String
from marshmallow.validate import Length, OneOf, Range

import lib.utils.hapi_excrypt_map as ExcryptMap
from lib.utils.string_utils import string_is_hex

from .approval_requests import ListApprovalRequests
from .shared_schemas import Hex, LdapLoginMixin, RequestId
from .shared_schemas import StringEnum as Enum
from .shared_schemas import (
    Subject,
    UniqueId,
    V3ExtensionSet,
    require_exactly_one,
    require_not_together,
)


class PKIOptions(Schema):
    DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    dnProfile = fields.String()
    dnProfileId = fields.String()
    extensionProfile = fields.String(required=True)
    randomPassphrase = fields.Boolean(missing=False)
    passphrase = fields.String(validate=[string_is_hex, Length(min=2)])
    subject = Subject()
    expiration = fields.DateTime(format=DATE_TIME_FORMAT)
    v3Extensions = V3ExtensionSet()
    exportPkcs12 = fields.Boolean(missing=False)
    savePkiKey = fields.Boolean(missing=False)

    @validates_schema
    def validate_passphrase(self, data, **kwargs):
        randomPassphrase = data.get("randomPassphrase", None)
        passphrase = data.get("passphrase", None)

        if not passphrase and not randomPassphrase:
            error_message = "Must specify passphrase if randomPassphrase disabled."
            field_list = "passphrase"

            raise ValidationError(error_message, field_list)

    @validates_schema
    def validate_exportOptions(self, data, **kwargs):
        exportPkcs12 = data.get("exportPkcs12", None)
        savePkiKey = data.get("savePkiKey", None)

        if exportPkcs12 and savePkiKey:
            error_message = "Cannot export PKCS #12 if saving PKI key pair."
            field_list = "exportPkcs12"

            raise ValidationError(error_message, field_list)

    @post_load  # Do after validation because field may not be present if subject is a string-type
    def validate_subject(self, data, **kwargs):
        if not ("dnProfile" in data or "dnProfileId" in data or "subject" in data):
            error_message = "Must specify at least one."
            field_list = "subject, dnProfile, dnProfileId"

            raise ValidationError(error_message, field_list)
        return data


class KeyOptions(Schema):
    algorithm = fields.String(validate=OneOf(["RSA", "ECC"]), required=True)
    modulus = fields.Integer(validate=(Range(min=512, max=4096), lambda m: m % 8 == 0))
    curve = fields.String(validate=OneOf(ExcryptMap.ECCCurveType.keys()))
    _validate_exactly_one = require_exactly_one("curve", "modulus")

    @validates_schema
    def validate_algorithm(self, data, **kwargs):
        algorithm = data.get("algorithm", None)
        if algorithm == "RSA":
            if data.get("curve", None):
                error_message = "Must specify modulus if algorithm is RSA."
                raise ValidationError(error_message, "modulus")
        else:
            if data.get("modulus", None):
                error_message = "Must specify curve if algorithm is ECC."
                raise ValidationError(error_message, "curve")


class CreatePkiGenerationRequest(LdapLoginMixin, Schema):
    policyId = UniqueId()
    pkiTree = fields.String()
    signingCert = fields.String()
    name = fields.String(required=True)
    hashType = fields.String(required=True, validate=OneOf(ExcryptMap.AsymHashTypes.keys()))
    approvalGroup = fields.String()
    commonNameAsSan = fields.Boolean(missing=False)
    pkiOptions = fields.Nested(PKIOptions, required=True)
    keyOptions = fields.Nested(KeyOptions, missing={"algorithm": "RSA", "modulus": 2048})


class ListPkiGenerationRequests(ListApprovalRequests):
    _object_filters = ["x509"]

    class Meta:
        exclude = ["objectSigning"]


class RetrievePkiGenerationRequest(Schema):
    requestId = fields.String(required=True)
    format = Enum(["DER", "PEM"], missing="PEM")


class UpdatePkiGenerationRequest(Schema):
    class UpdatePKIOptions(Schema):
        DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

        expiration = DateTime(format=DATE_TIME_FORMAT)
        extensionProfile = String()
        passphrase = Hex()
        randomPassphrase = Boolean()
        subject = Subject()
        v3Extensions = V3ExtensionSet()

        _validate_passphrase = require_not_together("passphrase", "randomPassphrase")

    requestId = RequestId(required=True)
    newName = String()
    hashType = Enum(ExcryptMap.AsymHashTypes)
    pkiOptions = Nested(UpdatePKIOptions)
