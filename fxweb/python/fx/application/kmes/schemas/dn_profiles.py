"""
@file      kmes/schemas/dn_profiles.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas related to /dn-profiles API endpoint
"""

from marshmallow import Schema, fields

from .shared_schemas import UniqueId, require_exactly_one


class RetrieveDNProfile(Schema):
    name = fields.String()
    id = UniqueId()

    _check_required = require_exactly_one("id", "name")
