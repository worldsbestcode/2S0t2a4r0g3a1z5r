"""
@file      kmes/schemas/pki_trees.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /api/pkitrees endpoint
"""

from marshmallow import Schema, ValidationError, fields, validates_schema
from marshmallow.validate import Length, OneOf

from lib.utils.hapi_excrypt_map import PermissionScope, PkiCertType

from .shared_schemas import Enum, PaginationMixin, PermissionsMap, UniqueId, require_exactly_one


class CreatePKITree(Schema):
    name = fields.String(
        required=True,
        validate=Length(min=1, max=30),
    )
    pkiType = Enum(
        PkiCertType,
        missing=PkiCertType.X509CertLocal,
        exclude=(
            PkiCertType.SCSARoot,
            PkiCertType.SCSAUpperLevel,
        ),
    )
    apiCredential = fields.String()

    @validates_schema
    def check_credential(self, data, **kwargs):
        # Don't try to send empty string as the name
        if data.get("apiCredential") == "":
            del data["apiCredential"]

        pki_type = data.get("pkiType")
        is_cloud_type = pki_type in (
            PkiCertType.X509CertExternalDigiCert,
            PkiCertType.X509CertExternalWCCE,
        )
        has_cloud_credential = "apiCredential" in data
        if has_cloud_credential and not is_cloud_type:
            raise ValidationError(
                "Field cannot be combined with pkiType '%s'" % pki_type, "apiCredential"
            )
        elif is_cloud_type and not has_cloud_credential:
            raise ValidationError("Field required for pkiType '%s'" % pki_type, "apiCredential")


class ListPKITrees(Schema, PaginationMixin):
    pass


class RetrievePKITree(Schema):
    id = UniqueId()
    name = fields.String()
    _validate_exactly_one = require_exactly_one("id", "name")


class UpdatePKITree(Schema):
    id = UniqueId()
    name = fields.String()
    newName = fields.String()
    _has_reference = require_exactly_one("id", "name")


class DeletePKITree(Schema):
    id = UniqueId()
    name = fields.String()
    _has_reference = require_exactly_one("id", "name")


class RetrievePKITreePermissions(Schema):
    id = UniqueId()
    name = fields.String()
    _has_reference = require_exactly_one("id", "name")


class UpdatePKITreePermissions(Schema):
    id = UniqueId()
    name = fields.String()
    permissions = PermissionsMap(required=True)
    updateChildren = fields.String(
        validate=OneOf(PermissionScope.names),
        missing="None",
    )
    _has_reference = require_exactly_one("id", "name")
