from flask import Flask
from rkweb.session_config import init_session_config

import os

class BaseApp(Flask):
    def __init__(self, app_name, api_name, api_title, api_version, api_class):
        """
        Initialize the Flask application

        Args:
            app_name: The name of the application
            api_name: The name of the API (/api_name/)
            api_title: The name for the API documentation
            api_version: the version number of the API (Ex: 1)
            api_class: The type of the API class to instantiate
        """
        super().__init__(app_name)

        # Configuration
        self.config['PROPAGATE_EXCEPTIONS'] = True
        self.config['PREFERRED_URL_SCHEME'] = 'https'
        # ISOs are currently almost 1.5GB large
        self.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024

        # Documentation
        self.config["API_TITLE"] = api_title
        self.config["API_VERSION"] = "v{}".format(api_version)
        self.config["OPENAPI_VERSION"] = "3.0.2"
        self.config["OPENAPI_JSON_PATH"] = "docs.json"
        self.config["OPENAPI_URL_PREFIX"] = "/{}/v{}/docs".format(api_name, api_version)
        self.config["OPENAPI_REDOC_PATH"] = "/{}/v{}/redoc".format(api_name, api_version)
        self.config["OPENAPI_SWAGGER_UI_PATH"] = ""
        self.config["OPENAPI_SWAGGER_UI_URL"] = "/shared/static/swagger-ui-3.51.1/"
        self.config["OPENAPI_SWAGGER_UI_CONFIG"] = {
            'persistAuthorization': True,
        }

        # Session config
        init_session_config(self)

        # REST API
        self.api = api_class(self)

