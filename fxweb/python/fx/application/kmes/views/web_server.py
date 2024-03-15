"""
@file      kmes/views/web_server.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for Web Server Settings
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses


class WebServer(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "WebServer")

    def get(self):
        data = request.args
        response = self.translate("Retrieve", data)

        status, message = response.pop("status", "Y"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)

    def put(self):
        data = request.get_json()
        response = self.translate("Update", data)

        status, message = response.pop("status", "Y"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.bad_request(message=message)


class Restart(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "WebServer")

    def post(self):
        request_data = request.get_json()
        response = self.translate("RestartWebserver", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success("Web Server successfully restarted", response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.bad_request(message)
