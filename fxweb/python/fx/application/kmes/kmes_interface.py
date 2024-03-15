"""
@file      kmes/kmes_interface.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2019

@section DESCRIPTION
A server interface to communicate with a KMES
"""

from rk_host_application.rk_host_application_server_interface import (
    RKHostApplicationServerInterface,
)


class KmesServerInterface(RKHostApplicationServerInterface):
    def __init__(self, program):
        super(KmesServerInterface, self).__init__(program)

    def login_user(self, server_request):
        return super(KmesServerInterface, self).login_user(server_request)
