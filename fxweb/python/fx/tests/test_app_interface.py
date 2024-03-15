"""
@file      test_app_interface.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Tests the base app interface class
"""

import collections
import unittest
import nose2
import nose.tools as nt

import fx
from app_config import AppConfig
from app_interface import AppInterface

class TestAppInterface(unittest.TestCase):
    """
    Application Interface test class
    """
    @classmethod
    def setUpClass(klass):
        pass

    @classmethod
    def tearDownClass(klass):
        pass

    def setUp(self):
        config = AppConfig()
        self.interface = AppInterface(config)

    def tearDown(self):
        pass

    def runTest(self):
        pass


    def test_make(self):
        """
        Tests make
        """
        obj = object()
        interface = self.interface
        interface._make_app = lambda : obj
        nt.eq_(obj, interface.make(), 'Application does not equal expected value')
        nt.ok_(interface.app, 'Application was not set')


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
        test_named = collections.namedtuple('TestNamed', ['arg0', 'arg1'])
        self.interface.named = test_named
        self.interface.args = [0, 1]
        args = self.interface.args
        nt.assert_tuple_equal(args, self.interface.named(0, 1))
