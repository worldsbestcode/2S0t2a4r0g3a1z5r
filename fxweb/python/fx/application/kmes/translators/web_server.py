"""
@file      kmes/translators/web_server.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for Web Server Settings
"""

import kmes.schemas.web_server as Schemas
from base.base_translator import BaseTranslator


class Retrieve(BaseTranslator):
    """
    JSON to Excrypt map to retrieve web server settings
    """

    request_schema = Schemas.Retrieve()

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "webserver:get",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "HN": "hostname",
            "VS": ("remoteSessions", int),
        }

        super().__init__(
            server_interface,
            "WebServer",
            "SETT",
            response_map=response_map,
            fixed_values=fixed_values,
        )


class Update(BaseTranslator):
    """
    JSON to Excrypt map to retrieve web server settings
    """

    request_schema = Schemas.Update()

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "webserver:modify",
        }

        request_map = {
            "hostname": "HN",
            "remoteSessions": "VS",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(
            server_interface, "WebServer", "SETT", request_map, response_map, fixed_values
        )


class RestartWebserver(BaseTranslator):
    """
    Restart the werbserver.
    """

    request_schema = None

    def __init__(self, server_interface):
        fixed_values = {"OP": "webserver:restart"}
        response_map = {"AN": "status", "BB": "message"}

        super().__init__(
            server_interface,
            "WebServer",
            "SETT",
            response_map=response_map,
            fixed_values=fixed_values,
        )
