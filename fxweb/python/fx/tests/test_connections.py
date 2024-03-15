"""
@file      test_connections.py
@author    James Espinoza (jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Unit tests to test connections and connection handler
"""
import gevent
from gevent.server import StreamServer

import unittest
from nose.tools import *
from mock import MagicMock, PropertyMock

import connection_handler
from app_config import AppConfig
from middleware_context import MiddlewareContext
from middleware_connection import MiddlewareConnection
from connection_handler import MiddlewareConnectionHandler
from librk import ExcryptMessage

TEST_CONN = ('127.0.0.1', 16001)
TIMEOUT = 1


class TestStreamServer(StreamServer):
    def __init__(self, address=TEST_CONN):
        super(TestStreamServer, self).__init__(listener=address)

    def handle(self, socket, address):
        print("Handling message " + str(address))

        running = True
        while running:
            line = socket.recv(1024)

            print("Read line " + str(line))

            if not line:
                break

            line = line.strip()
            em = ExcryptMessage(line)

            if em.getCommand() == "ECHO":
                print("Sending echo response")
                response = "[AOECHO;BJPONG!;]"
            elif em.getCommand() == "EXIT":
                print("Sending exit response")
                response = "[AOEXIT;ANY;]"

            em_response = ExcryptMessage(response)
            if em.hasField("AG"):
                em_response.setFieldAsString("AG", em.getField("AG"))

            socket.sendall(em_response.getText())


class TestConnections(unittest.TestCase):

    def setUp(self):
        self.server = TestStreamServer()
        self.server.start()
        self.config = AppConfig()
        self.config.generate_key()
        self.context = MiddlewareContext('', TEST_CONN, self.config, 'test')
        self.connection = MiddlewareConnection(self.context, True)

    def tearDown(self):
        self.connection.close()
        self.server.close()

    def test_connect_and_echo_conn_data_recv(self):
        self.connection.send("[AOECHO;]")
        response = self.connection.conn_data.recv()
        self.connection.close()

        assert_equals(response, "[AOECHO;BJPONG!;]")

    def test_connect_and_echo_receive(self):
        self.connection.send("[AOECHO;]")
        response = self.connection.receive()
        self.connection.close()

        assert_equals(response[0], "[AOECHO;BJPONG!;]")

    def test_invalid_connection(self):
        connection = MiddlewareConnection(self.context, False)
        assert_equals(connection.get_connection(), None)


class TestConnectionHandler(unittest.TestCase):
    def setUp(self):
        self.server = TestStreamServer()
        self.server.start()
        self.config = AppConfig()
        self.config.generate_key()
        self.ch = MiddlewareConnectionHandler(self.config)
        self.context = MiddlewareContext('', TEST_CONN, self.config, 'test')
        self.connected = self.ch.connect(self.context)

    def tearDown(self):
        self.ch.remove(self.context)
        self.server.close()

    def test_connect_and_store_conn(self):
        assert_true(self.connected)

    def test_connect_and_send_message(self):
        self.ch.send(self.context, "[AOECHO;]")
        response = self.ch.receive(self.context)
        assert_equals(response, ["[AOECHO;BJPONG!;]"])

    def test_connect_and_send_synch_message(self):
        mock = MagicMock()
        connection_handler.RespondHandler = mock
        mock().responses.__getitem__.return_value = '[AOECHO;AG1;]'
        response = self.ch.send_synch(self.context, "[AOECHO;]", TIMEOUT)
        mock.assert_called()
        mock().responses.__len__.assert_called()
        mock().responses.__getitem__.assert_called_once_with(0)
        mock().result.get.assert_called_once_with(block=True, timeout=TIMEOUT)
        assert_equals(response, '[AOECHO;AG1;]')

