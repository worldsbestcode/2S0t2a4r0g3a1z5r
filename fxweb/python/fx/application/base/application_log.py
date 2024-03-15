"""
@file      application_log.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
A syslog wrapper for log normalization
"""
import syslog


LOG_NAMES = {
    syslog.LOG_CRIT:      'CRITICAL',
    syslog.LOG_DEBUG:     'DEBUG',
    syslog.LOG_ERR:       'ERROR',
    syslog.LOG_INFO:      'INFO',
    syslog.LOG_WARNING:   'WARNING',
}


class LogDecorator(object):
    """
    Decorator for contructing the log calls
    """
    def __init__(self, level):
        """
        :param level the log level this decorator logs at
        """
        self.level = level
        self.name = LOG_NAMES.get(level, 'INFO')

    def _internal_log(self, message):
        """
       :param message the message to log to syslog
       :param level of the log
        """
        syslog.syslog(self.level, '{} {}'.format(self.name, message))

    def __call__(self, function):
        """
        Returns the inner log function of this decorator object
        :param function being wrapped
        """
        return self._internal_log


class ApplicationLogger(object):
    DEFAULT = syslog.LOG_INFO
    running = False

    """
    The middleware logging class
    """
    @classmethod
    def name_to_level(cls, level_name):
        """
        Does a reverse lookup on the dictionary for the syslog level
        :param level_name the name to reverse lookup in the dict
        """
        level_name = level_name.upper()
        for level, name in LOG_NAMES.items():
            if name == level_name:
                return level

        cls.debug('Log level not found')
        return cls.DEFAULT

    @classmethod
    def run(cls, log_name='fxweb', level_name='info'):
        """
        :param log_name the application name  (used as the syslog tag)
            NOTE: Do not change this without verifying that any relevant syslog
                  rules have been updated.
        :param level_name the log level string
        """
        if cls.running:
            return

        level = cls.name_to_level(level_name)
        log_name = log_name.replace(' ', '')
        cls.__begin(log_name, level)
        cls.running = True
        cls.info('{} application started'.format(log_name))

    @classmethod
    def __begin(cls, name, level):
        """
        Start the syslog
        :param name the application name
        :param level the log level enum
        """
        options = syslog.LOG_PID
        if level == syslog.LOG_DEBUG:
            options = syslog.LOG_PID | syslog.LOG_CONS
        else:
            syslog.setlogmask(syslog.LOG_UPTO(level))

        syslog.openlog(name, logoption=options)

    @staticmethod
    @LogDecorator(syslog.LOG_CRIT)
    def critical(_):
        """
        Calls log critical using the dectorator
        """
        pass

    @staticmethod
    @LogDecorator(syslog.LOG_DEBUG)
    def debug(_):
        """
        Calls log debug using the dectorator
        """
        pass

    @staticmethod
    @LogDecorator(syslog.LOG_ERR)
    def error(_):
        """
        Calls log error using the dectorator
        """
        pass

    @staticmethod
    @LogDecorator(syslog.LOG_INFO)
    def info(_):
        """
        Calls log info using the dectorator
        """
        pass

    @staticmethod
    @LogDecorator(syslog.LOG_WARNING)
    def warn(_):
        """
        Calls log warning using the dectorator
        """
        pass
