"""
@file      kmes/schemas/extension_profiles.py
@author    Dalton McGee(dmcgee@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Schemas for the KMES X.509 V3 Extension Profiles
"""

from marshmallow import Schema, ValidationError, fields, post_load, validates, validates_schema
from marshmallow.validate import Length, OneOf

from fx.lib.utils.hapi_excrypt_map import V3ExtensionModes
from .shared_schemas import (
    PaginationMixin,
    PermissionsMap,
    UniqueId,
    V3Extension,
    V3ExtensionSet,
    check_dict_for_duplicates,
    require_exactly_one,
)


class CombinedExtension:
    """Container for an extension and description"""
    def __init__(self, oid, extension, mode):
        self.oid = oid
        self.extension = extension if mode != "Restricted" else None
        self.description = {
            "oid": self.oid.dotted_string,
            "mode": mode
        }


class ExtensionAndDescription(V3Extension):
    value = fields.String()
    critical = fields.Boolean()
    mode = fields.String(required=True, validate=OneOf(V3ExtensionModes.keys()))

    @validates_schema
    def validate_mode_and_value(self, request, **kwargs):
        if request["mode"] == "Restricted" and "value" in request:
            raise ValidationError("Restricted OIDs cannot have a value.", "value")
        if request["mode"] != "Restricted" and "value" not in request:
            raise ValidationError("Missing data for required field.", "value")

    @validates_schema
    def validate_mode_and_critical(self, request, **kwargs):
        if request["mode"] == "Restricted" and "critical" in request:
            raise ValidationError("Restricted OIDs cannot have critical.", "critical")

        # sets missing critical value for all non-restricted extensions.
        request.setdefault("critical", False)


    @post_load
    def make_extension_object(self, extension, **kwargs) -> CombinedExtension:
        oid = extension["oid"]
        mode = extension["mode"]

        # The extension only exists if not restricted
        ext = None
        if mode != "Restricted":
            ext = super().make_extension_object(extension, **kwargs)

        return CombinedExtension(oid, ext, V3ExtensionModes.get(mode))


class CreateX509ExtensionProfile(Schema):
    name = fields.String(validate=Length(min=1, max=30), required=True)
    v3Extensions = V3ExtensionSet(ext_class=ExtensionAndDescription, required=True)
    allowUserDefined = fields.Boolean(missing=False)


class ListX509ExtensionProfile(Schema, PaginationMixin):
    pass


class LocateProfileMixin:
    id = UniqueId()
    name = fields.String(validate=Length(min=1, max=30))
    _validate_identifier_provided = require_exactly_one("id", "name")
    _type = fields.Constant("V3EXT_PROFILE")


class RetrieveX509ExtensionProfile(Schema, LocateProfileMixin):
    pass


class UpdateX509ExtensionProfile(Schema, LocateProfileMixin):
    newName = fields.String(validate=Length(min=1, max=30))
    v3Extensions = V3ExtensionSet(ext_class=ExtensionAndDescription)
    allowUserDefined = fields.Boolean()


class DeleteX509ExtensionProfile(Schema, LocateProfileMixin):
    pass


class RetrieveX509ExtensionPermissions(Schema, LocateProfileMixin):
    pass


class UpdateX509ExtensionPermissions(Schema, LocateProfileMixin):
    permissions = PermissionsMap(required=True)
