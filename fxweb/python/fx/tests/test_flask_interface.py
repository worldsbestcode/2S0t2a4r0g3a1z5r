"""
@file      test_flask_interface.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Tests the flask interface class
"""

import collections
import unittest
import nose.tools as nt

from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO

import fx
from flask_interface import FlaskInterface
from app_config import AppConfig


class TestFlaskInterface(unittest.TestCase):
    """
    Flask Interface test class
    """
    @classmethod
    def setUpClass(klass):
        pass

    @classmethod
    def tearDownClass(klass):
        pass

    def setUp(self):
        config = AppConfig()
        config.set('flask', 'uwsgi', False)
        self.interface = FlaskInterface(config)

    def tearDown(self):
        pass

    def runTest(self):
        pass

    def test_make(self):
        """
        Tests make
        """
        interface = self.interface
        interface.make()
        nt.assert_is_instance(interface.app, Flask)
        nt.assert_is_instance(interface.login, LoginManager)
        nt.assert_is_instance(interface.socket, SocketIO)
        nt.eq_(interface.app.debug, interface.args.debug)

    def test_args(self):
        """
        Tests the args getter
        """
        args = self.interface.args
        nt.ok_(args is not None, 'Args is None')
        nt.assert_is_instance(args, self.interface.named)

    def test_args_setter(self):
        """
        Tests the args setter
        """
        self.interface.args = range(4)
        args = self.interface.args
        nt.assert_tuple_equal(args, self.interface.named(*range(4)))
