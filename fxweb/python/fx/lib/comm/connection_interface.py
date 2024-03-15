"""
@file      connection_interface.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Wraps the communication in an interface to send and receive messages
with the server this class should not do direct translation
"""
from abc import ABCMeta, abstractmethod

class ConnectionInterface(metaclass=ABCMeta):
    DEFAULT_TIMEOUT = 10.0

    """ A thin wrapper around connections"""
    def __init__(self, context, conn):
        """
        @param context: Has all important information for connection creation
        @param connection: The actual connection object
        """
        self.context = context
        self.__conn = conn

    @abstractmethod
    def send(self, message):
        """
        Base class send
        """
        pass

    @abstractmethod
    def receive(self):
        """
        Base class receive
        """
        pass

    @abstractmethod
    def close(self):
        """
        Base class close
        """
        pass

    @abstractmethod
    def connect(self):
        """
        Base class connect
        """
        pass
