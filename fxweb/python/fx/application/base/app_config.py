"""
@file      app_config.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Handles the programs configuration
"""
import os

import psycopg2

from application_log import ApplicationLogger as Log
from configparser import ConfigParser
from database_factory import DatabaseFactory
from socket_address import SocketAddress
from lib.utils.fx_decorators import RetryOnException

from rkweb.rkserver import ServerConn

# Contains tuples of app_type, name, comm_type
BASE_CONFIG = {
        'guardian': ('flask', 'Guardian',                         'robot'),
        'byok':     ('flask', 'Guardian BYOK',                    'robot'),
        'regauth':  ('flask', 'Registration Authority',           'robot'),
        'kmes':     ('flask', 'Key Management Enterprise Server', 'robot'),
}


class AppConfig(ConfigParser):
    # Let server_type be accessed statically
    server_type = None

    """
    A subclass of config parser used to wrap any frequently used calls
    or constants
    """
    def __init__(self, config_file=None):
        """
        Create a configuration instance from config_file
        """
        ConfigParser.__init__(self)  # ConfigParser is an old style class in python2

        # Pull config file from environment if not provided
        if not config_file:
            config_file = os.getenv("FXWEB_CONFIG")
        print("FXWEB CONFIG: {}".format(config_file))

        self.read(config_file)
        self._set_server_type()
        self._add_hidden_properties()
        self.generate_key()

        self.__jwt_headers = ['Authorization']
        self.__api_key_headers = ['X-API-Key']

    def get_app_options(self, fields):
        """
        Returns a dictionary of key value pairs for the app type
        @return options the diction of key value pairs
        """
        items = dict(self.items(self.app_type))
        return [items[field] for field in fields]

    @property
    def app_type(self):
        """
        Get the application type
        """
        return self.get('base', 'app_type')

    @property
    def name(self):
        """
        Get a human readable application name
        @return self.__name
        """
        return self.get('base', 'name')

    @property
    def db_name(self):
        """
        Get the database name
        """
        return self.get('base', 'db_name')

    @property
    def log_level(self):
        """
        Get the human readable log level
        """
        return self.get('log', 'level')

    @property
    def server_type(self):
        """
        Gets the server type essentially what type of middleware we are
        """
        return AppConfig.server_type

    @property
    def comm_type(self):
        """
        Gets what communication backend we are using
        """
        return self.get('base', 'comm_type')

    @property
    def key(self):
        """
        Retrieves the app's secret key.
        """
        return self.__key

    @property
    def send_tag(self):
        return self.get('comm', 'context_tag', fallback='ST')

    @property
    def receive_tag(self):
        return self.get('comm', 'context_receive', fallback='SR')

    @property
    def jwt_headers(self):
        """Get a copy of the JWT header list"""
        return self.__jwt_headers[:]

    @property
    def api_key_headers(self):
        """Get a copy of the API Key header list"""
        return self.__api_key_headers[:]

    @property
    def host_address(self):
        """Get the host connection address"""
        client = True
        if self.get('comm', 'socktype') == 'api':
            client = False
        socket = ServerConn.get_sockfile(client)
        return SocketAddress.unix(address=socket)

    def _set_server_type(self):
        AppConfig.server_type = self.get('base', 'server_type')

    def _add_hidden_properties(self):
        """
        Add any properties that aren't public
        """
        fields = 'app_type', 'name', 'comm_type'
        for field, value in zip(fields, BASE_CONFIG[self.server_type]):
            self.set('base', field, value)

    def generate_key(self):
        """
        Generates a new random key for HMAC.
        """
        # This is a SHA-2 strength HMAC key
        self.__key = os.urandom(32)

    @RetryOnException(catch=psycopg2.Error, logger=Log.warn, log_msg='Failed to connect to database, retrying...')
    def load_database_options(self):
        """Load configuration parameters from the database"""
        factory = DatabaseFactory(self.db_name)
        database = factory.database_from_server_type(self.server_type)

        if database is not None:
            self.__jwt_headers = database.get_jwt_headers()
            self.__api_key_headers = database.get_api_key_headers()

    # Global configuration instance
    __config_instance = None

    @classmethod
    def set_config(cls, config):
        """Set the configuration instance"""
        cls.__config_instance = config

    @classmethod
    def get_config(cls):
        """Return the configuration instance"""
        if cls.__config_instance is None:
            cls.set_config(AppConfig())

        return cls.__config_instance
