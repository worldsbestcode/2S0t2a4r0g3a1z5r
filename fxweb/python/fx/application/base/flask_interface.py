"""
@file      flask_interface.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION

Wraps the flask application
"""

import os
import collections
import flask
import flask_login
import flask_socketio
from datetime import timedelta
from flask_cors import CORS
from flask_session import Session

import fx
from _path import WEB_BASE
from app_interface import AppInterface
from auth import User
from exception_registry import ExceptionRegistry
from base_exceptions import UserNotAuthenticated
from lib.utils.string_utils import parse_boolean
from rkweb.session_config import init_session_config

class FlaskInterface(AppInterface):
    """
    A wrapper around the flask application
    """

    flask_args = collections.namedtuple('FlaskApp',
        ['template_folder', 'static_folder', 'url', 'debug'])

    default_args = {
            'template_folder': ',',
            'static_folder': WEB_BASE,
            'url': '',
            'debug': True
    }

    def __init__(self, config):
        """
        Initializes the flask app with debugging arguments
        """
        super(FlaskInterface, self).__init__(config)
        self.named = FlaskInterface.flask_args
        self.args = self.named(**self.default_args)
        self.__login = None
        self.__socket = None
        self.unauthorized_uri = '/'
        self.server_type = config.server_type

    def _make_app(self):
        """
        Concrete implementation of application constructor
        """
        template, static, url, debug = self.args
        app = flask.Flask(__name__, template_folder=template, static_folder=static if static else WEB_BASE, static_url_path=url)
        app.debug = parse_boolean(debug)
        app.permanent_session_lifetime = timedelta(minutes=60)
        CORS(app, resource={r"/v0/key-encrypt/client/*": {"origins": "*",
                                            "allow_header": "Content-Type",
                                            "methods": ["GET", "POST"]}})
        self.__login = self._make_login(app)
        self.__socket = self._make_socket(app)

        # rkweb sessions
        init_session_config(app)

        return app

    def _make_socket(self, app, timeout=120):
        path = '/' + self.server_type + '/socket.io';
        """Instantiates the socket property"""
        if self.config.get('flask', 'uwsgi'):
            return flask_socketio.SocketIO(app, async_mode='gevent_uwsgi',
                                           ping_timeout=timeout, path=path)

        # Fallback if we aren't an uwsgi app
        return flask_socketio.SocketIO(app, ping_timeout=timeout, path=path)

    def _post_make(self):
        """
        Tasks for after the app is made
        """
        ExceptionRegistry(self)

    def _tear_down(self):
        """
        Removes the login manager and socketio instances
        """
        self.__login = None
        self.__socket = None

    @property
    def login(self):
        """
        Getter for LoginManager
        """
        return self.__login

    @property
    def config_section(self):
        """
        Return the name of the configuration section
        """
        return 'flask'

    @property
    def socket(self):
        """Return The socket propety"""
        return self.__socket

    def _make_login(self, app):
        """Construct and Configure the login manager
        :param app: The flask application
        :return: The new login manager
        """
        login = flask_login.LoginManager()
        login.init_app(app)
        User.init_login(login, app, UserNotAuthenticated("User not authenticated"))
        return login
