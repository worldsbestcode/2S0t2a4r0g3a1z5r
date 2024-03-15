import copy

from abc import ABC, abstractmethod

from flask_smorest import Api
from flask_smorest.utils import prepare_response
from apispec.ext.marshmallow import MarshmallowPlugin, OpenAPIConverter

from marshmallow import fields, Schema
import marshmallow_dataclass.union_field

from rkweb.swagger import swagger_ui
from rkweb.base_schema import ErrorResponse
from rkweb.ipc import IpcError, handle_ipc_error

from rkweb.login import LoginBlueprint, LogoutBlueprint

class FxConverter(OpenAPIConverter):
    def nested2properties(self, field, ret):
        # hook into this to add oneOf for lilmodel Union types
        if isinstance(field, marshmallow_dataclass.union_field.Union):
            options = ret.setdefault('oneOf', [])
            for model, schema in field.union_fields:
                if isinstance(schema, fields.Nested):
                    options.append(self.resolve_nested_schema(schema.schema))
                elif isinstance(schema, Schema):
                    options.append(self.resolve_nested_schema(schema))
                else:
                    options.append(self.field2property(schema))
            return ret

        return super().nested2properties(field, ret)

class FxMarshmallowPlugin(MarshmallowPlugin):
    Converter = FxConverter

class BaseApi(Api, ABC):
    def __init__(self, app):
        super().__init__(
            app=app,
            spec_kwargs={
                'marshmallow_plugin': FxMarshmallowPlugin(),
                'servers': [
                    {
                        'url': '/'
                    },
                ],
                'security': [
                    {
                        "type": "apiKey",
                        "name": "api_key",
                        "in": "X-API-Key",
                    },
                    {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    },
                ],
            },
        )
        self.api_version = int(app.config['API_VERSION'][1:])
        self.register_routes()

        self.add_blueprint(LoginBlueprint())
        self.add_blueprint(LogoutBlueprint())

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

    @abstractmethod
    def get_api_name(self) -> str:
        ...

    @abstractmethod
    def register_routes(self):
        ...

    def add_blueprint(self, blp, version = (1, None)) -> None:
        # None = only current API version
        if not version:
            blp.url_prefix = "/" + self.get_api_name() + "/v" + str(self.api_version) + blp.url_prefix
        # Tuple version range
        elif isinstance(version, tuple):
            min_version = version[0]
            max_version = version[1]
            if not max_version:
                max_version = self.api_version
            for v in range(min_version, max_version + 1):
                blp2 = copy.deepcopy(blp)
                blp2.name += " v" + str(v)
                self.add_blueprint(blp2, v)
            return
        # Specific integer version
        elif isinstance(version, int):
            blp.url_prefix = "/" + self.get_api_name() + "/v" + str(version) + blp.url_prefix
        # Custom
        else:
            blp.url_prefix = "/" + self.get_api_name() + str(version) + blp.url_prefix
        self.register_blueprint(blp)

