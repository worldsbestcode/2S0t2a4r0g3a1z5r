"""
@file      kmes/schemas/echo.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /api/echo endpoint
"""

from marshmallow import Schema, fields


class Echo(Schema):
    message = fields.String()
