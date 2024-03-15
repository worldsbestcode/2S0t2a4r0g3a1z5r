"""
@file      kmes/views/features.py
@author    Jamal Al (jal@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES features view
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses


class Features(ServerTranslatedView):
    """
    View class for Features
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Features")

    def get(self):
        """
        Retrieve Application and firmware features
        """

        data = request.args
        response = self.translate("Retrieve", data)
        status, message = response.pop("status", "N"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(message=message, body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)
