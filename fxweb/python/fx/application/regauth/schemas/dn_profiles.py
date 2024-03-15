"""
@file      regauth/schemas/dn_profiles.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /dn-profiles API endpoint
"""

from marshmallow import Schema, ValidationError, fields, validates_schema

from .shared_schemas import require_exactly_one


__all__ = [
    'RetrieveDNProfile',
]


class RetrieveDNProfile(Schema):
    name = fields.String()
    id = fields.String()

    _check_required = require_exactly_one('id', 'name')
