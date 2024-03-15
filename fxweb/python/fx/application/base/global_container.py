"""
@file      global_container.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Holds global objects
"""
from cache import Cache
from uri_router import URIRouter
from app_config import AppConfig
from interface_factory import InterfaceFactory
from librk import PyRKProgram
from auth import User
from application_log import ApplicationLogger


class GlobalContainer(PyRKProgram):
    """
    A container for global objects
    The singleton should be called instead of module objects
    Only things that must have a single instance belong in this class
    """
    def __init__(self, program_config=None, init_log=True):
        """
        Empty Initializer
        """
        super(GlobalContainer, self).__init__()
        config = program_config if program_config is not None else AppConfig.get_config()

        # Initialize logging before we do anything else
        if init_log:
            ApplicationLogger.run(level_name=config.log_level)

        # Make sure our config is the global one
        AppConfig.set_config(config)

        self.app_interface = InterfaceFactory.app_from_config(config)


        self.app = self.app_interface.app
        self.config = self.app_interface.config
        self.app_type = self.config.app_type
        self.server_type = self.config.server_type
        self.cache = Cache()
        self.router = None
        self.server_interface = InterfaceFactory.server_from_program(self)
        self.add_optional_objects()


    def add_optional_objects(self):
        """ Adds objects that only exist sometimes should only be called in concrete instances
            These should be moved to app_interfaces when possible
        """
        self.router = URIRouter(self)

    def run(self):
        """ Initializes The web application """
        if self.router:
            self.router.run()
        self.app_interface.run()

    def getFeatures(self):
        pass

    def getMountableDevice(self, iConnectionID):
        pass

