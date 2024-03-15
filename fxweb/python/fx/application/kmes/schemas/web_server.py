"""
@file      kmes/schemas/web_server.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to Web Server Settings
"""

from marshmallow import Schema, fields
from marshmallow.validate import Range


class Retrieve(Schema):
    pass


class Update(Schema):
    hostname = fields.Url(require_tld=False)
    remoteSessions = fields.Integer(validate=Range(1, 10))
