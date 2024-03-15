"""
@file      kmes/schemas/certificates.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /api/certificates endpoint
"""

from marshmallow import Schema, ValidationError, fields, validates_schema
from marshmallow.validate import Length, OneOf, Range

import lib.utils.hapi_excrypt_map as ExcryptMap
from lib.utils.string_utils import string_is_hex

from .shared_schemas import ALIAS_VALIDATOR, PermissionsMap, SecurityUsage
from .shared_schemas import StringEnum as Enum
from .shared_schemas import (
    Subject,
    UniqueId,
    V3ExtensionSet,
    ValidityPeriod,
    require_exactly_one,
    require_not_together,
)


class CertificateRetrievalMixinNoAlias:
    id = UniqueId()
    name = fields.String(validate=Length(min=1, max=80))
    pkiTree = fields.String(validate=Length(min=1, max=30))
    pkiTreeId = UniqueId()

    _must_have_identifier = require_exactly_one("id", "name")
    _id_and_tree_are_exclusive = require_exactly_one("id", "pkiTree", "pkiTreeId")


class CertificateRetrievalMixinNoTreeId:
    id = UniqueId()
    name = fields.String(validate=Length(min=1, max=80))
    alias = fields.String(validate=ALIAS_VALIDATOR)
    pkiTree = fields.String(validate=Length(min=1, max=30))

    _must_have_identifier = require_exactly_one("id", "name", "alias")
    _id_and_tree_are_exclusive = require_exactly_one("id", "pkiTree")


class CertificateRetrievalMixin(CertificateRetrievalMixinNoTreeId):
    pkiTreeId = UniqueId()
    _must_have_identifier = require_exactly_one("id", "name", "alias")
    _id_and_tree_are_exclusive = require_exactly_one("id", "pkiTree", "pkiTreeId")


class ParentRetrievalMixin:
    parentId = UniqueId()
    parent = fields.String(validate=Length(min=1, max=80))
    pkiTree = fields.String(validate=Length(min=1, max=30))
    pkiTreeId = UniqueId()

    _only_one_parent_field = require_not_together("parent", "parentId")
    _require_one_tree_field = require_exactly_one("pkiTree", "pkiTreeId")


class BasicConstraints(Schema):
    ca = fields.Boolean(required=True)
    pathLength = fields.Integer(validate=Range(0))
    critical = fields.Boolean(missing=False)

    @validates_schema
    def check_required(self, data, **kwargs):
        if "pathLength" in data and not data.get("ca"):
            raise ValidationError("Must be enabled to set a path length", "ca")


class CreateX509PkiOptions(Schema):
    hashType = Enum(ExcryptMap.RKGCHashTypes.names)
    subject = Subject()
    v3Extensions = V3ExtensionSet()
    validityPeriod = fields.Nested(ValidityPeriod)


class KeyOptions(Schema):
    securityUsage = SecurityUsage()
    majorKey = Enum(ExcryptMap.MajorKeys, missing="PMK")
    keyUsage = Enum(ExcryptMap.KeyUsage.Asymmetric)
    algorithm = Enum(("RSA", "ECC"), missing="RSA")
    exponent = fields.Integer()
    modulus = fields.Integer()
    curve = Enum(ExcryptMap.ECCCurveId.names)

    @validates_schema
    def rsa_or_ecc_fields(self, data, **kwargs):
        # Need to check for mismatched fields because RKGC reuses the tags
        rsa = data.setdefault("algorithm", "RSA") == "RSA"
        if "curve" in data and rsa:
            raise ValidationError("Cannot be combined with RSA", "curve")
        if "modulus" in data and not rsa:
            raise ValidationError("Cannot be combined with ECC", "modulus")
        if "exponent" in data and not rsa:
            raise ValidationError("Cannot be combined with ECC", "exponent")


class CreateX509(Schema, ParentRetrievalMixin):
    type = fields.String()
    alias = fields.String()
    pkiOptions = fields.Nested(CreateX509PkiOptions, required=True)
    keyOptions = fields.Nested(
        KeyOptions,
        missing=lambda: dict(majorKey="PMK", algorithm="RSA"),
    )


class RetrieveCertificate(Schema, CertificateRetrievalMixinNoTreeId):
    pass


class DeleteCertificate(Schema, CertificateRetrievalMixin):
    pass


class ExportCertificate(Schema, CertificateRetrievalMixinNoTreeId):
    filename = fields.String()
    format = Enum(["DER", "PEM", "JSON"], missing="PEM")


class CreateAlias(Schema, CertificateRetrievalMixinNoAlias):
    alias = fields.String(validate=ALIAS_VALIDATOR, required=True)


class ListAliases(Schema, CertificateRetrievalMixinNoAlias):
    pass


class DeleteAlias(Schema):
    # Delete alias doesn't support lookup by certificate name
    alias = fields.String(validate=ALIAS_VALIDATOR, required=True)
    id = UniqueId()
    pkiTree = fields.String(validate=Length(min=1, max=30))
    pkiTreeId = UniqueId()

    _id_and_tree_are_exclusive = require_exactly_one("id", "pkiTree", "pkiTreeId")


class ArchiveRestore(Schema):
    pkiTreeId = UniqueId()
    parentId = UniqueId()
    childrenOnly = fields.Boolean()
    # jsonFilter = fields.String()  TODO: uncomment when feature implemented
    applyToAll = fields.Boolean()
    _operation = fields.String(validate=OneOf(("archive", "restore")))

    XOR_validator = require_exactly_one("pkiTreeId", "parentId", "applyToAll")


class ImportX509(Schema, ParentRetrievalMixin):
    type = fields.String()
    data = fields.String(required=True)
    keyOptions = fields.Nested(
        KeyOptions, only=("majorKey", "keyUsage"), missing=lambda: dict(majorKey="PMK")
    )
    _require_one_tree_field = require_exactly_one("parentId", "pkiTree", "pkiTreeId")


class ImportEMV(ImportX509):
    name = fields.String(required=True)
    _require_one_tree_field = require_exactly_one("parentId", "pkiTree", "pkiTreeId")


class RetrieveCertPermissions(Schema, CertificateRetrievalMixinNoTreeId):
    _must_have_identifier = require_exactly_one("id", "name")


class UpdateCertPermissions(RetrieveCertPermissions):
    permissions = PermissionsMap(required=True)
    updateChildren = fields.String(validate=OneOf(ExcryptMap.PermissionScope.names), missing="None")


class GenerateEmvCert(Schema, CertificateRetrievalMixinNoTreeId):
    class CertFields(Schema):
        pan = fields.String(required=True)
        expiration = fields.String(validate=Length(min=4, max=4), required=True)
        sda = fields.String(validate=string_is_hex, required=True)

    def multiple_of_8(int):
        if int % 8 != 0:
            raise ValidationError("Value must be a multiple of 8")

    # TODO add uuid support
    pkiTree = fields.String(validate=Length(min=1, max=30), required=True)
    exponent = fields.String(validate=[string_is_hex, Length(min=1, max=6)])
    modulus = fields.Integer(validate=[multiple_of_8, Range(min=512, max=2040)])
    certOne = fields.Nested(CertFields, required=True)
    certTwo = fields.Nested(CertFields)

    _must_have_identifier = require_exactly_one("name", "alias")
