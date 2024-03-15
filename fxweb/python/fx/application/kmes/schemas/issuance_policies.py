"""
@file      kmes/schemas/issuance_policies.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to Issuance Policies
"""

from marshmallow import Schema
from marshmallow.fields import Boolean, DateTime, Integer, List, Nested, String
from marshmallow.validate import OneOf, Range

import lib.utils.hapi_excrypt_map as ExcryptMap

from .shared_schemas import (
    NameIdLink,
    PaginationMixin,
    UniqueId,
    require_exactly_one,
    require_implication,
    require_not_together,
    require_together,
)


class RetrieveIssuancePolicy(Schema):
    id = UniqueId()
    signingCertId = UniqueId()
    pkiTree = String()
    signingCert = String()

    # Not at_least because changing the signing cert of a policy isn't supported anyway:
    _unambiguous = require_exactly_one("id", "signingCertId", "signingCert")
    _ca_if_cert_name = require_together("signingCert", "pkiTree")


class Notifications(Schema):
    class Setting(Schema):
        enabled = Boolean(required=True)
        smtpTemplate = String(required=True)

    approval = Nested(Setting)
    denial = Nested(Setting)
    upload = Nested(Setting)


class ObjectSigning(Schema):
    enabled = Boolean()
    paddingModes = List(String(validate=OneOf(ExcryptMap.SignaturePadding)))


class X509Signing(Schema):
    class KeyType(Schema):
        type = String(required=True, validate=OneOf(("RSA", "ECC")))
        min = Integer(required=True)
        max = Integer(required=True)

    class ValidityPeriod(Schema):
        class MaxDuration(Schema):
            UNITS = {"Day", "Days", "Week", "Weeks", "Month", "Months", "Year", "Years"}
            unit = String(required=True, validate=OneOf(UNITS))
            amount = Integer(required=True, validate=Range(0))

        maxDuration = Nested(MaxDuration)
        expiration = DateTime(format="%Y-%m-%d")

    enabled = Boolean()
    allowPkiGeneration = Boolean()
    allowRenewals = Boolean()
    extensionProfiles = List(NameIdLink)
    keyTypes = List(Nested(KeyType))
    saveCertificate = Boolean()
    validityPeriod = Nested(ValidityPeriod)


class IssuancePolicy(RetrieveIssuancePolicy):
    alias = String()
    approvalGroupId = UniqueId()
    approvalGroup = String()
    approvalsRequired = Integer(validate=Range(0, 5))
    hashTypes = List(String(validate=OneOf(ExcryptMap.AsymHashTypes)))
    notifications = Nested(Notifications)
    objectSigning = Nested(ObjectSigning)
    x509Signing = Nested(X509Signing)

    _regauth_name_or_id = require_not_together("approvalGroup", "approvalGroupId")


class ListIssuancePolicies(PaginationMixin, Schema):
    pkiTree = String()
    pkiTreeId = UniqueId()
    parent = String()
    parentId = UniqueId()
    x509Signing = Boolean()
    objectSigning = Boolean()
    pkiGeneration = Boolean()

    _allowed_perms = ExcryptMap.ObjectPermType.names - {ExcryptMap.ObjectPermType.ePermNone.name}
    _default_perm = ExcryptMap.ObjectPermType.ePermView.name
    permission = String(validate=OneOf(_allowed_perms), missing=_default_perm)

    _ca_if_cert_name = require_implication("parent", "pkiTree", "pkiTreeId")
    _not_uuid_and_name = require_not_together("parent", "parentId")
