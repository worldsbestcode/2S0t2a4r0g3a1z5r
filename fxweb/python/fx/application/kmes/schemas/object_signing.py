"""
@file      kmes/schemas/object_signing.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas for Object Signing Requests
"""

from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf, Range

from lib.utils.hapi_excrypt_map import AsymHashTypes, SignaturePadding
from lib.utils.string_utils import string_is_hex

from .approval_requests import ListApprovalRequests
from .shared_schemas import LdapLoginMixin, RequestId, UniqueId


class CreateObjSigningRequest(LdapLoginMixin, Schema):
    policyId = UniqueId()
    pkiTree = fields.String()
    signingCert = fields.String()
    name = fields.String(required=True, validate=Length(min=1, max=30))
    hashType = fields.String(required=True, validate=OneOf(AsymHashTypes.keys()))
    approvalGroup = fields.String(validate=Length(min=1, max=30))
    messageDigest = fields.String(required=True, validate=[Length(min=2, max=128), string_is_hex])
    paddingMode = fields.String(required=True, validate=OneOf(SignaturePadding.keys()))
    saltLength = fields.Integer(validate=Range(min=0, max=256))


class ListObjSigningRequests(ListApprovalRequests):
    _object_filters = ["objectSigning"]

    class Meta:
        exclude = ["x509"]


class RetrieveObjSigningRequest(Schema):
    requestId = RequestId(required=True)


class UpdateObjSigningRequest(Schema):
    requestId = RequestId(required=True)
    newName = fields.String(validate=Length(min=1, max=30))
    hashType = fields.String(validate=OneOf(AsymHashTypes.keys()))
    messageDigest = fields.String(validate=[Length(min=2, max=128), string_is_hex])
    paddingMode = fields.String(validate=OneOf(SignaturePadding.keys()))
    saltLength = fields.Integer(validate=Range(min=1, max=256))
