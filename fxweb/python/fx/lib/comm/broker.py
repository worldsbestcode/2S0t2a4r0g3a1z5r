"""
@file      broker.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
The broker exists as a translation layer to isolate command
processing from the views
"""
from abc import ABCMeta, abstractmethod


class Broker(object, metaclass=ABCMeta):
    """A class for processing messages"""

    def __init__(self, server_interface, context, user):
        self.__interface = server_interface
        self.__context = context
        self.__user = user

    @abstractmethod
    def process(self, request_data):
        """Preform method processing"""
        pass

    @property
    def interface(self):
        """Returns the application inteface"""
        return self.__interface

    @property
    def context(self):
        """Returns the connection context"""
        return self.__context

    @property
    def user(self):
        """Returns the user for this message if any"""
        return self.__user
