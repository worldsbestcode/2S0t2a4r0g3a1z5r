"""
@file      uri_router.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Sets up URI routes and views.
"""

from string import Template

import fx
from view_factory import ViewFactory
from application_log import ApplicationLogger as Log
from server_views import ServerLoginView, ServerLogoutView
from auth import RkWebBridge

class URIRoute(object):
    def __init__(self, program):
        self.program = program

    def setup_routes(self):
        pass


class FxURIRoute(URIRoute):
    def setup_routes(self):
        kw_args = dict(server_interface=self.program.server_interface)
        views = ViewFactory.get_views(self.program)
        http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

        for rule, view in list(views.items()):
            to_add = [method for method in http_methods if hasattr(view, method.lower())]

            Log.debug(f'Adding route {rule} {to_add}')
            as_view_inst = view.as_view(rule, **kw_args)
            self.program.app.add_url_rule(rule, view_func=as_view_inst,
                                          methods=to_add)

        self.init_rkweb_bridge()

    # Setup rkweb bridge so we can sync auth state
    def init_rkweb_bridge(self):
        def __login(jwt):
            login_data = {
                'authType': 'jwt',
                'authCredentials': {
                    'token': jwt,
                },
            }

            view = ServerLoginView(self.program.server_interface)
            view._login(login_data)

        RkWebBridge.set_login(__login)

        def __logout():
            view = ServerLogoutView(self.program.server_interface)
            view._logout()

        RkWebBridge.set_logout(__logout)



class URIRouter(object):
    """
    Handles setup of application's uri routes
    """

    def __init__(self, program):
        """
        Initialize the urirouter
        @param program passed to the individual routes for route setup
        """
        self.routes = []
        self.program = program

    def make_routes(self, program):
        """
        Creates the route objects from the server type
        @param webabb the global application
        """
        return [FxURIRoute(program)]

    def run(self):
        """ Begin routing """
        self.routes = self.make_routes(self.program)
        for route in self.routes:
            route.setup_routes()
