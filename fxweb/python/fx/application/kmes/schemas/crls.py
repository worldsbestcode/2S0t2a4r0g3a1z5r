"""
@file      kmes/schemas/crls.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Validation schemas for Certificate Revocation Lists
"""

from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf, Range

from lib.utils.hapi_excrypt_map import AsymHashTypes, CrlTimeUnits, RevocationReasons

from .shared_schemas import Enum, UniqueId, require_together


class BaseCrl(Schema):
    certId = UniqueId(required=True)
    hashType = fields.String(validate=OneOf(AsymHashTypes.keys()))
    interval = fields.Integer(validate=Range(min=1))
    intervalUnit = fields.String(validate=OneOf(CrlTimeUnits.keys()))
    overlap = fields.Integer(validate=Range(min=1))
    overlapUnit = fields.String(validate=OneOf(CrlTimeUnits.keys()))

    _validate_interval = require_together("intervalUnit", "interval")
    _validate_overlap = require_together("overlapUnit", "overlap")


class CreateCrl(BaseCrl):
    pass


class RetrieveCrl(BaseCrl):
    class Meta:
        fields = ["certId"]


class UpdateCrl(BaseCrl):
    pass


class DeleteCrl(BaseCrl):
    class Meta:
        fields = ["certId"]


class ExportCrl(BaseCrl):
    format = fields.String(validate=OneOf(["DER", "PEM", "JSON"]))
    filename = fields.String()

    class Meta:
        fields = ["certId", "format", "filename"]


class ImportCrl(BaseCrl):
    data = fields.String(required=True, validate=Length(min=1))

    class Meta:
        fields = ["certId", "data"]


class RevokeCert(BaseCrl):
    revokeCertId = UniqueId(required=True)
    reason = Enum(RevocationReasons, required=True)
    action = fields.String()

    class Meta:
        fields = ["certId", "revokeCertId", "reason", "action"]
