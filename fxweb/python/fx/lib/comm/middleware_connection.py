"""
@file      middleware_connection.py
@author    James Espinoza (jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
This class implements connect, close, send, receive for ExcryptMessage
"""
import socket
from threading import Lock
import fx
from fx_ssl import (
    SSLInfo,
    SSLWrappedAddress,
)

from connection_interface import ConnectionInterface
from conn_exceptions import (
    CannotConnectException,
    ErrorOnReadException,
    ErrorOnWriteException
)


class MiddlewareConnection(ConnectionInterface):
    """
    Connection class that implements sending, receiving, connecting, closing connections
    Parses incoming ExcryptMessages
    """
    def __init__(self, context, connect_now=True, ssl_info=None):
        if ssl_info is None:
            ssl_info = SSLInfo()

        self.target = SSLWrappedAddress(context.to_address, ssl_info)

        # Parse to connection target address
        conn = self._create_connected_socket() if connect_now else None
        self.conn_data = ConnectionData(conn=conn)

    def receive(self):
        """
        Parses all data received from the server
        Returns:
            Parsed message buffer
        """
        try:
            buff = self.conn_data.recv()
        except socket.error:
            raise ErrorOnReadException('Could not read message from {}'.format(self.conn_data))

        messages = []
        work = self.conn_data.dangling + buff

        # TODO rewrite to allow for standard messages
        while b']' in work and b'[' in work:
            start = work.find(b'[')
            end = work.find(b']')
            next_message = work[start:end+1]
            # Bad buffer, extra [
            if b'[' in next_message[1:]:
                bad_index = next_message.find(b'[')
                work = work[bad_index+1:]
            else:
                work = work[end+1:]
                # Bad buffer, extra ]
                if end < start:
                    pass
                else:
                    messages.append(next_message)

        self.conn_data.dangling = work

        return messages

    def send(self, message):
        """
        Sends a data blob to the endpoint
        Args:
            message: The data to send
        """
        try:
            self.conn_data.send(message)
        except socket.error:
            error = 'Error sending message with length {} on {}.'
            error = error.format(len(message), self.conn_data)
            raise ErrorOnWriteException(message)

    def connect(self):
        """
        Opens a connection to the specified host/port
        """
        self.close()
        self.conn_data.conn = self._create_connected_socket()

    def close(self):
        """
        Closes the current connection
        """
        if self.conn_data.conn:
            self.conn_data.conn.close()
            self.conn_data.conn = None

    def _create_connected_socket(self):
        """ Builds a new socket for a connection
        :return: The new socket
        :raises: CannotConnectException if ssl cannot connect
        """
        conn = self.target.new_socket()
        conn.setblocking(False)
        conn.settimeout(ConnectionInterface.DEFAULT_TIMEOUT)

        try:
            self.target.connect_socket(conn)
        except socket.error:
            raise CannotConnectException(f'Error connecting to {self.target}')
        return conn

    def get_fd(self):
        return self.conn_data.conn.fileno()


class ConnectionData:
    """
    Class that holds meta data for connection object
    """
    MAX_RECV = 1024*1024

    def __init__(self,
                 timeout=ConnectionInterface.DEFAULT_TIMEOUT,
                 conn=None):
        """
        Contructor for ConnectionData
        Args:
            timeout: The timeout on connections
            conn: connection object for this context
        """
        self.conn = conn
        self.dangling = b''
        self.mutex = Lock()
        self.timeout = timeout

    def __str__(self):
        if self.conn is not None:
            return 'Connection {}'.format(self.conn.fileno())
        else:
            return 'Unknown Connection'

    def clear_buffers(self):
        """
        Clears any buffers when we send a new command
        """
        self.dangling = b''

    def send(self, message, timeout=None):
        """
        Send a single message
        Args:
            message: A single message
            timeout: Message timeout
        """
        data = message.encode()
        timeout = timeout if timeout is not None else self.timeout
        with self.mutex:
            self.conn.settimeout(float(timeout))
            self.conn.sendall(data)

    def recv(self):
        """
        Receives from the connection buffer
        """
        with self.mutex:
            data = self.conn.recv(self.MAX_RECV)

        return data
