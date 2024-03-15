from flask_smorest import Api
from flask_smorest.utils import prepare_response
from apispec.ext.marshmallow import MarshmallowPlugin, OpenAPIConverter

from swagger import swagger_ui
from base_schema import ErrorResponse
from ipc import IpcError, handle_ipc_error

from login import LoginBlueprint
from devices import DevicesBlueprint
from balancing_ports import BalancingPortsBlueprint

class FxMarshmallowPlugin(MarshmallowPlugin):
    Converter = OpenAPIConverter

class GuardianApi(Api):
    def __init__(self, app):
        super().__init__(app=app, spec_kwargs={'marshmallow_plugin': FxMarshmallowPlugin()})
        self.api_version = app.config['API_VERSION']
        self.register_routes()

        # Set default error response schema
        response = {
            "description": "Default error response",
            "schema": ErrorResponse(),
        }
        prepare_response(response, self.spec, self.DEFAULT_RESPONSE_CONTENT_TYPE)
        self.spec.components.responses.pop("DEFAULT_ERROR")
        self.spec.components.response("DEFAULT_ERROR", response, lazy=False)

        # Top level error handler when IPC throws an error
        app.register_error_handler(IpcError, handle_ipc_error)

    def _openapi_swagger_ui(self):
        return swagger_ui(self)

    def register_routes(self):
        self.add_blueprint(LoginBlueprint())
        self.add_blueprint(DevicesBlueprint())
        self.add_blueprint(BalancingPortsBlueprint())

    def add_blueprint(self, blp):
        # Prepend the API version
        if len(self.api_version) > 0:
            blp.url_prefix = "/" + self.api_version + blp.url_prefix
        self.register_blueprint(blp)

