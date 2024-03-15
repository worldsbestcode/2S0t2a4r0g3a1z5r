"""
@file      regauth/schemas/certificate_signing_requests.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /api/certificates/signing-requests endpoint
"""

from marshmallow import Schema, fields, post_load, validates_schema
from marshmallow import ValidationError
from marshmallow.decorators import pre_load
from marshmallow.validate import OneOf, Length

import lib.utils.hapi_excrypt_map as ExcryptMap
from lib.utils.string_utils import string_is_hex
from .shared_schemas import Subject, V3Extension


__all__ = [
    'CreatePKIRequest',
]


class PKIOptions(Schema):
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    dnProfile = fields.String()
    dnProfileId = fields.String()
    extensionProfile = fields.String(required=True)
    keyType = fields.String(
        required=True,
    )
    randomPassphrase = fields.Boolean(missing=False)
    passphrase = fields.String(
        validate=[string_is_hex, Length(min=2)]
    )
    subject = Subject()
    certExpiration = fields.DateTime(format=DATE_TIME_FORMAT)
    v3Extensions = fields.List(
        fields.Nested(V3Extension),
        validate=Length(max=10),
    )
    exportPkcs12 = fields.Boolean(missing=False)
    savePkiKey = fields.Boolean(missing=False)

    @pre_load
    def coerce_key_type(self, data, **kwargs):
        ECCCurveNames = ['ECC 192', 'ECC 224', 'ECC 256', 'ECC 384', 'ECC 521']

        # Legacy support, first release required input to be "ECC 512" which is not a supported curve
        # silently convert ECC 512 to 521 so it doesn't error
        # First release permitted only ECC 521
        if data.get('keyType') == 'ECC 512':
            data['keyType'] = 'ECC 521'

        keyType = data.get('keyType')
        if not keyType.startswith('RSA ') and not keyType in ECCCurveNames:
            raise ValidationError('Invalid key type', 'keyType')

        return data

    @post_load  # Do after validation because field may not be present if subject is a string-type
    def validate_subject(self, data, **kwargs):
        if not ('dnProfile' in data or 'dnProfileId' in data or 'subject' in data):
            error_message = 'Must specify at least one.'
            field_list = 'subject, dnProfile, dnProfileId'

            raise ValidationError(error_message, field_list)
        return data

    @post_load # do after validation so extensions are serialized to objects
    def validate_oids_unique(self, data, **kwargs):
        extensions = data.get('v3Extensions', [])
        oids = set()
        for idx, extension in enumerate(extensions):
            if extension.oid in oids:
                reason = "Duplicate OID '%s' provided" % (extension.oid.dotted_string,)
                field = "v3Extensions.{}.id".format(idx)
                raise ValidationError(reason, field)
            oids.add(extension.oid)
        return data


class CreatePKIRequest(Schema):
    pkiTree = fields.String(required=True)
    signingCert = fields.String(required=True)
    requestName = fields.String(required=True)
    requestType = fields.String(
        required=True,
        validate=OneOf(ExcryptMap.CertRequestTypes.keys())
    )
    hashType = fields.String(
        required=True,
        validate=OneOf(ExcryptMap.AsymHashTypes.keys())
    )
    approvalGroup = fields.String(required=True)
    ldapUsername = fields.String()
    ldapPassword = fields.String(
        validate=[string_is_hex, Length(min=2)]
    )
    commonNameAsSan = fields.Boolean(missing=False)
    renewalCheck = fields.Boolean(missing=False)
    subjectAltNames = fields.List(
        fields.String(),
    )
    pkiOptions = fields.Nested(
        PKIOptions,
        required=True
    )
