from flask import Flask
from flask_session import Session

import os
import hashlib
import base64
from datetime import timedelta

from api import GuardianApi
from token_thread import TokenThread

class App(Flask):
    def __init__(self):
        super().__init__(__name__)

        # Configuration
        self.config['PROPAGATE_EXCEPTIONS'] = True

        # Documentation
        self.config["API_TITLE"] = "Guardian Management"
        self.config["API_VERSION"] = "v1"
        self.config["OPENAPI_VERSION"] = "3.0.2"
        self.config["OPENAPI_JSON_PATH"] = "docs.json"
        self.config["OPENAPI_URL_PREFIX"] = "/v1/docs"
        self.config["OPENAPI_REDOC_PATH"] = "/v1/redoc"
        self.config["OPENAPI_SWAGGER_UI_PATH"] = ""
        self.config["OPENAPI_SWAGGER_UI_URL"] = "/static/swagger-ui-3.51.1/"
        self.config["OPENAPI_SWAGGER_UI_CONFIG"] = {
            'persistAuthorization': True,
        }

        # Store sessions on local filesystem
        self.config['SESSION_TYPE'] = 'filesystem'
        self.config['SESSION_FILE_DIR'] = '/tmp/flask/guardian'
        self.config['SESSION_USE_SIGNER'] = True
        self.config['SESSION_KEY_PREFIX'] = "Guardian"
        # Maximum number of concurrent sessions
        self.config['SESSION_FILE_THRESHOLD'] = 100 * 1000
        self.config['SESSION_FILE_MODE'] = 0o600
        self.config['SESSION_PERMANENT'] = True
        self.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours = 12)

        self.sess = Session()
        self.sess.init_app(self)
        self.init_seed()

        # Session token refresh thread
        self.token_thread = TokenThread(self.config)
        # TODO: Stops requests from being processes ~30% of the time
        #self.token_thread.start()

        # REST API
        self.api = GuardianApi(self)

    def init_seed(self):
        """
        Initialize the secret used to sign client session identifiers.
        Since the session state is stored server side, knowledge of this
        key does not give you the ability to manipulate session context.
        """
        self.secret_key = """
            ede2bc3ab68bf21b927ee88090ecffcdc60b12150959c2a868874aebe0fb1864
            14cb64f2cbaegad90c610fc4d1199a1f2hcff93c5207ce2e336b123328wf6d25
            2794d11a16c50e090e9b46e1cdb2b2e79d61d967e332463ea34c6d084dd56f19
            """

