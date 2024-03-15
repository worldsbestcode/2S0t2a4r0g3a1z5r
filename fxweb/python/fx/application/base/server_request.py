"""
@file      server_request.py
@author    James Espinoza (jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
A modifiable tuple to wrap requests
"""

class ServerRequest(object):
    """
    Class that stores data between View and Server Interface classes
    Not strongly defined to allow for arbitrary data to be passed between the two layers
    """
    def __init__(self, request, data, error = ""):
        self.request = request
        self.data = data
        self.error = error