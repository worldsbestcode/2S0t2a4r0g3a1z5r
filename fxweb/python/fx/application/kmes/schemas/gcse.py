"""
@file      kmes/schemas/gcse.py
@author    Stephen Jackson (sjackson@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /v0/key-encrypt/client/<keycommand> endpoint
"""

from marshmallow import Schema, fields

__all__ = [
    "GCSEWrap",
    "GCSEUnwrap",
]


class GCSEWrap(Schema):
    authentication = fields.String(required=True)
    authorization = fields.String(required=True)
    action = fields.String(required=True)
    plaintext = fields.String(required=True)
    addAuthData = fields.String(required=True)
    reason = fields.String()


class GCSEUnwrap(Schema):
    authentication = fields.String(required=True)
    authorization = fields.String()
    action = fields.String(required=True)
    wrappedBlob = fields.String(required=True)
    addAuthData = fields.String(required=True)
    reason = fields.String()
