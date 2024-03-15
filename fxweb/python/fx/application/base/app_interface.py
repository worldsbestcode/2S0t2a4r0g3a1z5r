"""
@file      app_interface.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Wraps a third party application allowing dynamic construction
References to the application should not point to the internal app
"""
import collections

from flask import Flask
from app_config import AppConfig
from application_log import ApplicationLogger

class AppInterface(object):
    """
    A thin wrapper around the application class to delay instantiation
    """

    def __init__(self, config: AppConfig):
        """
        Basic application initiation
        """
        self.__app = None
        self.__server = None
        self.__config = config

        self.named = collections.namedtuple('EmptyApp', [])
        self.__args = self.named()

    def make(self):
        """
        Make an instance of the application if none exists
        Also constructs any subparts
        """
        if not self.app:
            self._pre_make()
            self.__app = self._make_app()
            self._post_make()
        return self.app

    def run(self):
        """
        Starts the application
        """
        self.initialize_log()
        self.config.load_database_options()

    def initialize_log(self):
        """Initialize application log"""
        self.log.run(level_name=self.config.log_level)

    def reset(self):
        """
        Resets the app as long as nothing is holding
        references to the internal application
        """
        self.__app = None
        self._tear_down()

    def _pre_make(self):
        """
        Any premake action that may need to occur
        """
        if self.config is not None:
            self.args = self.config.get_app_options(self.named._fields)

    def _make_app(self):
        """
        This should be implemented in subclasses
        """
        raise NotImplementedError()

    def _post_make(self):
        """
        For anything that has to happen after the app has been made
        but before it is run
        """
        pass

    def _tear_down(self):
        """
        Extra application cleanup
        """
        pass

    @property
    def app(self) -> Flask:
        """
        Get the internal app structure
        """
        return self.__app

    @property
    def args(self):
        """
        Set the internal arguments
        """
        return self.__args

    @args.setter
    def args(self, args):
        """
        Set the argument list
        @param args   A collection with arguments to feed the named tuple
        """
        self.__args = self.named._make(args)

    @property
    def config(self):
        """
        Returns the configuration object
        """
        return self.__config

    @property
    def log(self):
        """
        Returns the application log class
        """
        return ApplicationLogger
