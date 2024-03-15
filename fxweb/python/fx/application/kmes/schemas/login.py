"""
@file      kmes/schemas/login.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /api/login endpoint
"""

from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from .shared_schemas import Base64String, excrypt_safe_validator


class AuthCredentials(Schema):
    username = fields.String(required=True)
    password = Base64String(required=True)
    _validate_excrypt_safe = excrypt_safe_validator(exclude=["password"])


class SubmitLogin(Schema):
    authType = fields.String(required=True, validate=OneOf(["userpass"]))
    authCredentials = fields.Nested(AuthCredentials, required=True)
    # Only needed by the GUI to delay login
    _loginNow = fields.Boolean(missing=True)
