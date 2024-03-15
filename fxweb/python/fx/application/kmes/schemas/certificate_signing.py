"""
@file      kmes/schemas/certificate_signing.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas for Certificate Signing Requests
"""

from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf

from lib.utils.hapi_excrypt_map import AsymHashTypes
from lib.utils.string_utils import string_is_hex

from .approval_requests import ListApprovalRequests
from .shared_schemas import LdapLoginMixin, RequestId, Subject, UniqueId, V3ExtensionSet


class PkiOptions(Schema):
    extensionProfile = fields.String()
    expiration = fields.DateTime(format="%Y-%m-%d")
    subject = Subject()
    v3Extensions = V3ExtensionSet()


class CreateCertSigningRequest(LdapLoginMixin, Schema):
    policyId = UniqueId(required=True)
    name = fields.String(required=True, validate=Length(min=1, max=30))
    hashType = fields.String(required=True, validate=OneOf(AsymHashTypes.keys()))
    approvalGroup = fields.String(validate=Length(min=1, max=30))
    signingRequest = fields.String(required=True, validate=string_is_hex)
    pkiOptions = fields.Nested(PkiOptions)


class ListCertSigningRequests(ListApprovalRequests):
    _object_filters = ["x509"]

    class Meta:
        exclude = ["objectSigning"]


class RetrieveCertSigningRequest(Schema):
    requestId = RequestId(required=True)


class UpdateCertSigningRequest(Schema):
    requestId = RequestId(required=True)
    newName = fields.String(validate=Length(min=1, max=30))
    hashType = fields.String(validate=OneOf(AsymHashTypes.keys()))
    signingRequest = fields.String(validate=string_is_hex)
    pkiOptions = fields.Nested(PkiOptions)
