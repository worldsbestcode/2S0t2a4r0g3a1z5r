"""
@file      server_interface.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Base server interface for communicating with a backend server
"""
from server_request import ServerRequest

class ServerInterface(object):
    def __init__(self, program):
        self.program = program

    def connect(self):
        """Connect to the server"""
        pass

    def send(self, server_request):
        pass
