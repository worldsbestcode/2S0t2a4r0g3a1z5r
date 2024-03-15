"""
@file      kmes/translators/dn_profiles.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Translators for KMES DN Profiles views
"""


import kmes.schemas.dn_profiles as schemas
from kmes.kmes_parsers import parse_subject
from base.base_translator import BaseTranslator


class RetrieveDNProfile(BaseTranslator):
    """
    JSON to Excrypt map for retrieving a DN profile with RAVD
    """

    request_schema = schemas.RetrieveDNProfile()

    def __init__(self, server_interface):
        # The translator for RAUP (CreatePKIRequest) uses this - update if you change things here
        request_map = {
            "name": "NA",
            "id": "ID",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "ID": "id",
            "DN": ("subject", parse_subject),
        }

        super().__init__(server_interface, "DNProfiles", "RAVD", request_map, response_map)
