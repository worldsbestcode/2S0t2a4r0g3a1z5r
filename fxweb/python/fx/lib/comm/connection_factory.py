"""
@file      connection_factory.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Creates connections from context
"""
import fx
from middleware_connection import MiddlewareConnection

class ConnectionFactory:
    @staticmethod
    def connection_from_context(context):
        """ Returns the connection type from the context """
        return MiddlewareConnection(context)

    @staticmethod
    def create_connection(context):
        """Create a connection"""
        return ConnectionFactory.connection_from_context(context)
