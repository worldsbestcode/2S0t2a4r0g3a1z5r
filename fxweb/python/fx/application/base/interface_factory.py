"""
@file      interface_factory.py
@author    Matthew Seaworth(mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Handles instantiation of swappable parts of the program
"""

import fx
from app_interface import AppInterface
from server_interface import ServerInterface
from flask_interface import FlaskInterface
from byok.byok_interface import ByokServerInterface
from guardian_server_interface import GuardianServerInterface
from regauth.regauth_interface import RAServerInterface
from kmes.kmes_interface import KmesServerInterface

APPLICATION_INTERFACES = {
    'default': AppInterface,
    'flask': FlaskInterface,
}

SERVER_INTERFACES = {
    'default': ServerInterface,
    'byok': ByokServerInterface,
    'regauth': RAServerInterface,
    'guardian': GuardianServerInterface,
    'kmes': KmesServerInterface
}

class InterfaceFactory(object):
    """
    A function to interact with application interfaces
    """

    @staticmethod
    def app_from_config(config) -> AppInterface:
        cls = InterfaceFactory.get_app_interface(config.app_type)
        interface = cls(config)
        interface.make()
        return interface

    @staticmethod
    def server_from_program(program) -> ServerInterface:
        server_type = program.config.server_type
        cls = InterfaceFactory.get_server_interface(server_type)
        return cls(program)

    @staticmethod
    def get_app_interface(app_type):
        app_interface = APPLICATION_INTERFACES.get(app_type, AppInterface)
        return app_interface

    @staticmethod
    def get_server_interface(server_type):
        server_interface = SERVER_INTERFACES.get(server_type, ServerInterface)
        return server_interface
