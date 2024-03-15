"""
@file      test_app_log.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Tests the base app logging
"""
import syslog
import mock
import unittest
import nose2
import fx
from application_log import (
    ApplicationLogger as Log,
    LogDecorator,
    LOG_NAMES
)


class TestAppLog(unittest.TestCase):
    BeginMock = mock.MagicMock()
    LogMock = mock.MagicMock()
    """
    Application Interface test class
    """
    @classmethod
    def setUpClass(cls):
        Log._ApplicationLogger__begin = cls.BeginMock
        LogDecorator._internal_log = cls.LogMock
        # Make all the function closures point to mocks

        def make_call(level):
            return staticmethod(LogDecorator(level)(None))

        Log.critical = make_call(syslog.LOG_CRIT)
        Log.debug = make_call(syslog.LOG_DEBUG)
        Log.error = make_call(syslog.LOG_ERR)
        Log.info = make_call(syslog.LOG_INFO)
        Log.warn = make_call(syslog.LOG_WARNING)

    def tearDown(self):
        self.BeginMock.reset_mock()
        self.LogMock.reset_mock()

    def test_run_calls_begin_known(self):
        """
        Tests run with a known string
        """
        name = 'test with known'
        Log.run(name, 'error')
        self.BeginMock.assert_called_once_with(name.replace(' ', ''), syslog.LOG_ERR)

    def test_run_calls_begin_unknown(self):
        """
        Tests run with an unknown string
        """
        name = 'test with unknown'
        Log.run(name, 'unknown')
        self.BeginMock.assert_called_once_with(name.replace(' ', ''), syslog.LOG_INFO)

    def test_error(self):
        msg = 'Error test string'
        Log.error(msg)
        self.LogMock.assert_called_once_with(msg)

    def test_debug(self):
        msg = 'Debug test string'
        Log.debug(msg)
        self.LogMock.assert_called_once_with(msg)

    def test_info(self):
        msg = 'Info test string'
        Log.info(msg)
        self.LogMock.assert_called_once_with(msg)

    def test_crit(self):
        msg = 'Critical test string'
        Log.critical(msg)
        self.LogMock.assert_called_once_with(msg)

    def test_log_decorator(self):
        msg = 'Log decorator test string'
        for level, name in LOG_NAMES.items():
            decorator = LogDecorator(level)
            self.assertEqual(decorator.level, level)
            log_func = decorator(None)
            log_func(msg)
            self.LogMock.assert_called_once_with(msg)
            self.LogMock.reset_mock()
