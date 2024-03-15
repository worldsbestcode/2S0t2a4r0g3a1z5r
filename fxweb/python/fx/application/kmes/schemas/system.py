"""
@file      kmes/schemas/system.py
@author    Jamal Al(jal@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to system API endpoint
"""

from datetime import date

from marshmallow import Schema, ValidationError, fields
from marshmallow.validate import Length, OneOf, Range

import lib.utils.hapi_excrypt_map as ExcryptMap

from .shared_schemas import UniqueId


class UpdateCertificates(Schema):
    pkiCacheSize = fields.Integer(validate=Range(100, 1000))
    expireNotification = fields.Integer(validate=Range(0, 99))
    allowDuplicateNames = fields.Boolean()
    allowInvalidCerts = fields.Boolean()
    appendRandom64Bit = fields.Boolean()


class UpdateAutoBackup(Schema):
    def validate_weekDays(days):
        for day in days:
            if days.count(day) > 1:
                raise ValidationError(f"Entry includes duplicate values {day}")

    enabled = fields.Boolean()
    sshKeys = fields.Boolean()
    cards = fields.Boolean()
    printers = fields.Boolean()
    beginDate = fields.Date()
    frequency = fields.Integer(validate=Range(min=1, max=52))
    weekDays = fields.List(
        fields.String(validate=OneOf(ExcryptMap.DaysOfWeek.keys())), validate=validate_weekDays
    )
    storageMirrors = fields.List(fields.String())


class UpdateGlobalPermissions(Schema):
    class Permission(Schema):
        type = fields.String(required=True)
        setting = fields.String(required=True)

    permissions = fields.List(fields.Nested(Permission))


class UpdateNtp(Schema):
    enabled = fields.Boolean()
    syncOnStartup = fields.Boolean()
    host = fields.String(validate=Length(0, 15))


class UpdateRaSettings(Schema):
    allowAnonymous = fields.Boolean()
    approvalType = fields.String(validate=OneOf(["USER", "GROUP"]))
    anonymousWcce = fields.Boolean()
    wccePolicy = UniqueId()


class UpdateSecureMode(Schema):
    pci = fields.Boolean()
    fips = fields.Boolean()
