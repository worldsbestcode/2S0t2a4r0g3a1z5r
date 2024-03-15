"""
@file      handler.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Implements generic handler for matched response messages
"""
from abc import ABCMeta, abstractmethod
from gevent.event import AsyncResult

class Handler(metaclass=ABCMeta):
    """
    A base handler class that abstracts out the handler interface
    """
    
    def __init__(self):
        self.responses = []

    @abstractmethod
    def handle(self, message, conn):
        """
        Handle method to process response
        :param message: Response message to process
        :param conn: Connection that the response was received from
        """
        pass

    def update_responses(self, message):
        """
        Update responses that have been matched
        :param message: Add matched message to the internal list
        """
        self.responses.append(message)

class RespondHandler(Handler):
    """
    Handler that sends an event to a waiting Greenlet to notify of
    a received message event
    """
    def __init__(self):
        super(RespondHandler, self).__init__()
        self.result = AsyncResult()

    def handle(self, message, conn):
        """
        Handle method that sends event to waiting Greenlet
        :param message: Message that matches the request
        :param conn: Connection that response was received on
        """
        self.result.set()

class ForwardHandler(Handler):
    """
    Forwarding handler that will send matched response to the connection associated
    with the passed in context
    :param send: Send method to send the response to
    :param context: Context of associated with connection to send response to
    """
    def __init__(self, send, context):

        super(ForwardHandler, self).__init__()
        self.send = send
        self.context = context

    def handle(self, message, conn):
        """
        Send response to it's destination
        :param message: Message that matches the request
        :param conn: Connection that response was received on
        """
        self.send(message, self.context)


