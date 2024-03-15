"""
@file      server_login_context.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Creates the middleware context for login
"""
import fx
from application_log import ApplicationLogger
from conn_exceptions import CannotConnectException
from middleware_context import MiddlewareContext


class ServerLoginContext:
    """Controls login context"""
    def __init__(self, server_interface):
        """Initialize this object
        Arguments:
            server_interface: the interface object
        """
        self.interface = server_interface
        program = self.interface.program
        self.config = program.config
        self.app = program.app

    def get_context(self, user):
        """Gets the current context associated with user
        Arguments:
            user: Current user that is logged in(or not)
        Returns:
            success: The success state
            context: The user context information
        """
        success = True
        context = user.context
        return success, context

    def create_middleware_context(self):
        """Creates a middleware context for a user"""
        context = self.generate_context()
        try:
            success = self.interface.connect(context)
        except CannotConnectException:
            ApplicationLogger.error('Failed to connect to server')
            success = False

        return success, context

    def generate_context(self):
        """
        Generates a fresh context object for a new connection
        """
        from_address = -1

        # TODO Create a ContextFactory for different types of context objects
        interface = self.interface
        return MiddlewareContext(
            from_address,
            self.config.host_address,
            self.config,
            self.app,
            self.config.send_tag,
            self.config.receive_tag
        )
