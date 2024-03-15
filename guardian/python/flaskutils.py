import http
from copy import deepcopy
from flask import request, jsonify, abort as _abort
from webargs import asyncparser
from flask_smorest import Blueprint as Blueprint_

from base_schema import BaseResponse, SchemaErrorResponse

def respond(code: int=200, data: dict=None):
    """
    Create and send response from data.
    This function does not return execution to the caller.

    Args:
        code: HTTP response code
        data: Response JSON data as dictionary
    """
    if not data:
        data = {}
    if "status" not in data:
        data["status"] = "Success" if code == 200 else "Failure"
    if "message" not in data:
        data["message"] = "Success"
    ret = jsonify(data)
    ret.status_code = code

    _abort(ret)
    assert False

def abort(code: int, message: str, data: dict=None):
    """
    Abort with special message.
    This function does not return execution to the caller.

    Args:
        code: HTTP return code
        message: Message to send back to user
        data: Response data
    """
    if not data:
        data = {}
    data["message"] = message
    respond(code, data)

# Makes flask smorest Blueprint work with async functions
class Blueprint(Blueprint_):
    ARGUMENTS_PARSER = asyncparser.AsyncParser()

    def fxroute(self, endpoint, method, schema=None, resp_schemas={}, description=None):

        def param_decorator(func):
            schema_instance = None
            if schema:
                schema_instance = schema()

            # Process view asynchronously
            async def wrapper(*args, **kwargs):
                ret = None
                # Parse out schema and pass it
                if schema_instance:
                    args = request.get_json(force=True)
                    errors = schema_instance.validate(args)
                    if errors:
                        return abort(422, "Validation error", {"errors": errors})
                    ret = await func(args)
                # Just process
                else:
                    ret = await func(*kwargs.values())

                return ret

            # The deepcopy avoids modifying the wrapped function doc
            wrapper._apidoc = deepcopy(getattr(wrapper, "_apidoc", {}))

            # Set default success model
            if 200 not in resp_schemas:
                resp_schemas[200] = BaseResponse

            # Set default schema validation error
            if 422 not in resp_schemas:
                resp_schemas[422] = SchemaErrorResponse

            # XXX: Stolen from Blueprint.arguments
            if schema:
                # At this stage, put schema instance in doc dictionary. Il will be
                # replaced later on by $ref or json.
                parameters = {
                    "in": "json",
                    "required": True,
                    "schema": schema,
                }
                if description is not None:
                    parameters["description"] = description
                try:
                    parameters["examples"] = schema_instance.examples
                except:
                    pass

                error_status_code = self.ARGUMENTS_PARSER.DEFAULT_VALIDATION_STATUS

                # Add parameter to parameters list in doc info in function object
                docs = wrapper._apidoc.setdefault("arguments", {})
                docs.setdefault("parameters", []).append(parameters)
                docs.setdefault("responses", {})[error_status_code] = http.HTTPStatus(
                    error_status_code
                ).name

            # XXX: Stolen from Blueprint.response
            resp_docs = {}
            for status_code in resp_schemas:
                resp_schema = resp_schemas[status_code]()

                # Document response (schema, description,...) in the API doc
                doc_schema = self._make_doc_response_schema(resp_schema)
                resp_description = http.HTTPStatus(int(status_code)).phrase
                try:
                    resp_description = resp_schema.description
                except:
                    pass
                resp_doc = {}
                resp_doc["schema"] = doc_schema
                resp_doc["description"] = resp_description
                try:
                    resp_doc["examples"] = resp_schema.examples
                except:
                    pass
                resp_doc["content_type"] = "application/json"

                resp_docs[status_code] = resp_doc

                # Add all success response codes
                if status_code >= 200 and status_code <= 299:
                    wrapper._apidoc.setdefault("success_status_codes", []).append(status_code)

            # Store doc in wrapper function
            wrapper._apidoc.setdefault("response", {})["responses"] = resp_docs

            # Remove default response error
            try:
                wrapper._apidoc["arguments"].pop("responses")
            except:
                pass

            # Register view with Flask
            register_view = self.route(rule=endpoint, methods=[method])
            register_view(wrapper)

            return wrapper

        return param_decorator

