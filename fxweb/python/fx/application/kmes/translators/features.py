"""
@file      kmes/translators/features.py
@author    Jamal Al (jal@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for KMES Features views
"""

import kmes.schemas.features as FeaturesSchemas
from base.base_translator import BaseTranslator
from kmes.kmes_parsers import parse_application_features, parse_firmware_features


class RetrieveFeatures(BaseTranslator):
    """
    JSON to Excrypt map to retrieve features
    """

    request_schema = FeaturesSchemas.RetrieveFeatures()

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "features:get",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "FE": ("application", parse_application_features),
            "FW": ("firmware", parse_firmware_features),
        }

        super().__init__(
            server_interface,
            "Features",
            "SETT",
            response_map=response_map,
            fixed_values=fixed_values,
        )
