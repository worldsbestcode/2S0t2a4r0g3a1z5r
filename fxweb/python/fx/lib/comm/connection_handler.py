"""
@file      connection_handler.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Interacts with connection objects and tracks open connections
"""
from abc import ABCMeta, abstractmethod
import select
import gevent
from gevent import Greenlet
from gevent.lock import BoundedSemaphore
from gevent.pool import Pool

import fx
from base_exceptions import MiddlewareException
from connection_interface import ConnectionInterface
from connection_factory import ConnectionFactory
from matcher import CountResponseMatcher, SynchResponseMatcher
from handler import RespondHandler
from asynccomm import synchronized
from application_log import ApplicationLogger as Log
from conn_exceptions import (
    ErrorOnReadException,
    ErrorOnWriteException,
    MissingConnectionException,
    ServerConnectionTimeout
)

class BaseConnectionHandler(metaclass=ABCMeta):
    """A wrapper around communication """
    def __init__(self, config):
        """
            Initialize the communication backend wrapper
            @param conn: the connection interface
            @param config: the application config
        """

    @abstractmethod
    def send(self, context, message):
        """
            Send a message without blocking
            @param message_context: Provides any extra information needed for sending the message
            @param message: The actual message to send
        """
        pass

    @abstractmethod
    def send_synch(self, context, message, timeout=ConnectionInterface.DEFAULT_TIMEOUT, matcher = None):
        """
            Send a message and blocks until the response is retrieved.
            @param context: Provides any extra information needed for sending the message
            @param message: The actual message to send
            @param timeout: Timeout value to fail on if exceeded
            @param matcher: Message matcher to use. If None, SynchResponseMatcher is used
            @return: Response message or None if timeout exceeded
        """
        pass

    @abstractmethod
    def send_asynch(self, context, message, timeout, handler, matcher = None):
        """
            Send a message and doesn't block. Processes matcher asynchronously, and continues processing
            @param context: Provides any extra information needed for sending the message
            @param message: The actual message to send
            @param timeout: Timeout value to fail on if exceeded
            @param matcher: Message matcher to use. If None, SynchResponseMatcher is used
        """
        pass

    @abstractmethod
    def receive(self, context):
        """
            Receive raw data without blocking
            @param message_context: Provides any extra information needed for sending the message
        """
        pass

    @abstractmethod
    def connect(self, context):
        """
            Connect to the server
            @param context: context for the message type to create
        """
        pass

    @abstractmethod
    def remove(self, context):
        """
            Removes connection using message_context
            @param context: the connection to remove
        """
        pass

    @abstractmethod
    def reset(self):
        """Clear all connections"""
        pass

    @abstractmethod
    def __get_connection(self, context):
        """
            Get a connection corresponding to a context
            Note : MUST be locked by the calling method!!!
        """
        pass

class MiddlewareConnectionHandler(Greenlet):
    """
    A connection handler class that will send messages and match their responses asynchronously
    The way a response is handled is determined by a handler object that is sent in with the message
    This functionality is modeled off the RK ConnectionHandler

    This class is subclassed from a Greenlet, which is a lightweight thread that allows
    processing of data concurrently(not in parallel). This allows the middleware to process commands
    asynchronously and handle multiple requests at once.
    """
    # Semaphore to protect open connection cache
    conn_semaphore = BoundedSemaphore(1)

    # Semaphore to protect pending message cache
    sent_data_semaphore = BoundedSemaphore(1)

    # Semaphore to protect message listener list
    message_listeners_semaphore = BoundedSemaphore(1)

    # Default Greenlet spawn count
    DEFAULT_GREENLET_COUNT = 100

    # Select timeout
    DEFAULT_SELECT_TIMEOUT = 1.0

    def __init__(self, config):
        """
            Initialize the communication backend wrapper
            @param config: the application config
        """
        # Init Greenlet base class
        Greenlet.__init__(self)

        # A dict of MiddlewareContext to ConnectionInterface objects. This is a cache that
        # stores currently open connections
        self.__connections = {}

        # A list of SentData objects. This is a cache of pending messages responses, their matchers, and handlers
        self.__sent_message_data = []

        # List of message listeners to notify for every message
        self.__message_listeners = []

        # A config object that holds the application config
        self.__config = config

        # A Greenlet pool. At max, the middleware will spawn this many Greenlets
        self.__pool = Pool(self.DEFAULT_GREENLET_COUNT)
        self.start()

    def _run(self):
        """
        A greenlet thread that monitors the currently connected sockets.
        This method will read the socket data, check if it matches, and spawn a greenlet
        to handle the reponse.
        """
        fd_to_conn = {}
        sockets = []

        while self.started:
            try:
                with MiddlewareConnectionHandler.conn_semaphore:
                    for conn in list(self.__connections.values()):
                        sockets.append(conn.get_fd())
                        fd_to_conn.update({ conn.get_fd() : conn })
            except gevent.timeout.Timeout:
                Log.warn('Timeout occured in connection handler lock.')
                continue

            try:
                ready_to_read, ready_to_write, in_error = \
                    select.select(sockets, [], sockets, self.DEFAULT_SELECT_TIMEOUT)
            except select.error:
                raise ErrorOnReadException('Could not select fd to read from.')

            try:
                self.__process_fds(fd_to_conn, ready_to_read, ready_to_write, in_error)

                fd_to_conn = {}
                sockets = []
            except:
                raise

    def __process_fds(self, fd_to_conn, ready_to_read, ready_to_write, in_error):
        """
        Reads in, matches, and handles data that has been received from a remote endpoint.
        Also closes fds that have been returned in error
        :param fd_to_conn: The map containing connection objects associated with fd
        :param ready_to_read: The set of fds that is ready to be read from
        :param ready_to_write: The set of fds that is ready to be written to(will never be used)
        :param in_error: The set of fds that is ready to be closed due to fd error
        """
        messages = []
        match_data = {}
        for read_fd in ready_to_read:
            try:
                messages = fd_to_conn[read_fd].receive()
            except ErrorOnReadException:
                in_error.append(read_fd)
                Log.warn("Error while reading from fd({0})".format(read_fd))
            except IndexError:
                in_error.append(read_fd)
                Log.error('Read from unknown fd({})'.format(read_fd))
            except AttributeError:
                in_error.append(read_fd)
                Log.error('Read from unknown fd({})'.format(read_fd))

            if len(messages) <= 0:
                Log.warn("Null data received while reading from fd({0})".format(read_fd))
                in_error.append(read_fd)
            else:
                for m in messages:
                    # Match messages
                    matched = self.__match_message(m)
                    if matched:
                        match_data.update(matched)

                    # Notify message listeners
                    with MiddlewareConnectionHandler.message_listeners_semaphore:
                        for listener in self.__message_listeners:
                            self.__pool.spawn(listener.handle(m, fd_to_conn[read_fd]))

                for (message, handler) in match_data.items():
                    self.__pool.spawn(handler.handle(message, fd_to_conn[read_fd]))

        for error_fd in in_error:
            Log.error("Closing socket due to disconnection from fd({0})".format(error_fd))
            with MiddlewareConnectionHandler.conn_semaphore:
                for context, conn in list(self.__connections.items()):
                    if conn.get_fd() == error_fd:
                        conn.close()
                        del self.__connections[context]

    @synchronized(sent_data_semaphore)
    def __match_message(self, message):
        """
        Helper method that checks if a message matches, checks if a matcher
        is completed, and handles the message if its matcher has completed

        :param message: Message to match against
        :return: dict of message to handler for completed matches
        """
        result = {}
        for sent_data in self.__sent_message_data:
            if sent_data.matcher and sent_data.matcher.matches(message):
                sent_data.matcher.update_match_status(message)
                sent_data.handler.update_responses(message)

                if sent_data.matcher.is_complete:
                    result.update({message:sent_data.handler})
                    self.__sent_message_data.remove(sent_data)

        return result

    def send(self, context, message):
        """
        Helper method to get a connection based on context and send a message to it
        Note: Does not return a response
        :param context: Context to retrieve connection
        :param message: Message to send
        """
        connection = self.__get_connection(context)
        connection.send(message)

    def send_synch(self, context, message, timeout=ConnectionInterface.DEFAULT_TIMEOUT, matcher = None):
        """
            Send a message blocking
            :param message_context: Provides any extra information needed for sending the message
            :param message: The actual message to send
            :exception gevent.timeout.Timeout: Raised if no response is received from the remote endpoint
                                              within the timeout period
            :exception MissingConnectionException: Raised if trying to send to a connection that doesn't exist
        """

        responses = None

        if self.exists(context):

            if not matcher:
                matcher = SynchResponseMatcher(context.get_resp_synch_tag(), context.inc_synch_value())
                message = matcher.init_match_status([context.get_req_synch_tag(), message])

            sd = SentData(matcher, RespondHandler(), message)

            # Cache SendData
            with MiddlewareConnectionHandler.sent_data_semaphore:
                self.__sent_message_data.append(sd)

            # Send the message
            with MiddlewareConnectionHandler.conn_semaphore:
                Log.debug(f'-> {message}')
                connection = self.__get_connection(context)
                if connection:
                    connection.send(message)


            # Wait for the response
            try:
                sd.handler.result.get(block=True, timeout=timeout)
                if (len(sd.handler.responses) > 1):
                    responses = sd.handler.responses
                else:
                    responses = sd.handler.responses[0]

            except gevent.timeout.Timeout:
                #TODO Parse and log message w/o sensitive data
                raise ServerConnectionTimeout('Timeout while sending message')
        else:
            raise MissingConnectionException('Attempted to access unknown connection.')

        Log.debug('<- ' + (b"".join(responses).decode('latin') if isinstance(responses, list) else responses.decode('latin')))

        return responses

    def send_asynch(self, context, message, timeout, handler, matcher = None):
        """
            Send a message without blocking
            :param message_context: Provides any extra information needed for sending the message
            :param message: The actual message to send
            :exception MissingConnectionException: Raised if trying to send to a connection that doesn't exist
        """
        # Init the SendData

        if not matcher:
            matcher = SynchResponseMatcher(context.get_resp_synch_tag(), context.inc_synch_value())

        if self.exists(context):
            sd = SentData(matcher, handler, message)
            message = sd.matcher.init_match_status(message)

            # Cache SendData
            with MiddlewareConnectionHandler.sent_data_semaphore:
                self.__sent_message_data.append(sd)

            # Send the message
            with MiddlewareConnectionHandler.conn_semaphore:
                connection = self.__get_connection(context)

                if connection:
                    try:
                        connection.send(message)
                    except:
                        raise ErrorOnWriteException('Could not send message to server.')
        else:
            raise MissingConnectionException()

    @synchronized(conn_semaphore)
    def receive(self, context):
        """
            Receive raw data without blocking
            @param message_context: Provides any extra information needed for sending the message
        """
        connection = self.__get_connection(context)
        data = connection.receive()
        return data

    def connect(self, context):
        """
            Connect to the server
            @param context: context for the message type to create
        """
        success = False

        connection = ConnectionFactory.create_connection(context)
        with MiddlewareConnectionHandler.conn_semaphore:
            if connection is not None:
                if context not in self.__connections:
                    self.__connections[context] = connection
                    success = True
                else:
                    connection.close()
        return success

    @synchronized(conn_semaphore)
    def remove(self, context):
        """
            Removes connection using message_context
            @param context: the connection to remove
        """
        if context in self.__connections:
            self.__connections[context].close()
            del self.__connections[context]

    @synchronized(conn_semaphore)
    def reset(self):
        """Clear all connections"""
        self.__connections = {}

    @synchronized(conn_semaphore)
    def exists(self, context):
        """Clear all connections"""
        conn = None
        try:
            conn = self.__get_connection(context)
        except KeyError:
            pass
        except:
            raise

        return conn != None

    def __get_connection(self, context):
        """
            Get a connection corresponding to a context
            Note : MUST be locked by the calling method!!!
                   Users should not be accessing the connection interface
                   objects external to the connection handler
        """
        return self.__connections[context]

    def add_message_listener(self, message_listener):
        with MiddlewareConnectionHandler.message_listeners_semaphore:
            self.__message_listeners.append(message_listener)

class SentData(object):
    """
    Metadata container for messages that are waiting for responses and have matchers
    associated with them
    :param matcher: The matcher to check the response against
    :param handler: The handler to handle the response with
    :param request: The original request that was sent
    """
    def __init__(self, matcher = None, handler = None, request = None):
        self.matcher = matcher
        self.handler = handler
        self.request = request

