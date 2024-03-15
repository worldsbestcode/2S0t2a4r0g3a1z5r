"""
@file      fx_view.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Base View for fx web
"""

from flask.views import MethodView
from flask import abort, request, jsonify

from server_request import ServerRequest

class FxView(MethodView):
    def __init__(self, server_interface):
        self.server_interface = server_interface


