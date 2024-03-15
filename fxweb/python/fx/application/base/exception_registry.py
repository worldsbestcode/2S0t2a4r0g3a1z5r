"""
@file      exception_registry.py
@author    Matthew Seaworth(mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Register the exceptions to the flask app in one swoop
"""
import fx
import rk_host_flask_handlers
from base_exceptions import BASE_EXCEPTIONS
from conn_exceptions import CONNECTION_EXCEPTIONS
from rk_exceptions import REMOTEKEY_EXCEPTIONS


class ExceptionRegistry(object):
    """
    Class to hold helper functions for exception initialization
    """
    def __init__(self, app_interface):
        """
        Initializes all exceptions
        :param app_interface the interface to the application
        """
        self.register_all(app_interface)

    @staticmethod
    def __register_exception(e_class, app, logger):
        """
        Function to register an exception
        :param e_class The class to register the exception for
        :param app The flask application
        """
        @app.errorhandler(e_class)
        def handle_exception(exception):
            """
            Send the proper exception handler
            """
            if logger is not None:
                exception.log_exception(logger)
            return exception._handle_exception(app)

        return handle_exception

    @staticmethod
    def create_exception_list(config):
        """
        Optionally add in desired exceptions
        :param config The global configuration
        """
        exceptions = []
        exceptions.extend(BASE_EXCEPTIONS)
        exceptions.extend(CONNECTION_EXCEPTIONS)
        if config.server_type in [
            'regauth',
            'guardian',
            'kmes'
        ]:
            exceptions.extend(REMOTEKEY_EXCEPTIONS)

        return exceptions

    def register_all(self, app_interface):
        """
        Function to do all the exception initialization
        :param app_interface the flask application interface
        """
        config = app_interface.config
        exceptions = self.create_exception_list(config)
        app = app_interface.app
        logger = app_interface.log
        for e_class in exceptions:
            self.__register_exception(e_class, app, logger)

        if config.server_type in ('regauth', 'kmes', 'byok'):
            rk_host_flask_handlers.set_error_handlers(app, config)
