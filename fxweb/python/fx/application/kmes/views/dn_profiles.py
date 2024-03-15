"""
@file      kmes/views/dn_profiles.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Implements the URI methods for the KMES DN Profiles view
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses


class DNProfiles(ServerTranslatedView):
    """
    View class for Distinguished Name Profiles
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "DNProfiles")

    def get(self):
        request_data = request.args

        response = self.translate("Retrieve", request_data)
        status, message = response.pop("status", "Y"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P" or message == "NO PERMISSION":
            return APIResponses.forbidden(message)
        elif "INVALID X.509 DN PROFILE" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.internal_error(message)
