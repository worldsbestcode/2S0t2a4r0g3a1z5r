"""
@file      kmes/views/logout.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES logout view
"""
from flask import jsonify
from flask_login import current_user, logout_user

from base.server_views import ServerTranslatedView
from auth import User


class Logout(ServerTranslatedView):
    decorators = []

    def __init__(self, server_interface):
        super(Logout, self).__init__(server_interface, None, None)

    def post(self, *args, **kwargs):
        self.server_interface.logout_user()

        if current_user is not None:
            # Remove the user session object and update the session cookie
            User.remove(current_user.get_id(), logout_user)

        return jsonify({"message": "Logged out", "status": "Success"})
