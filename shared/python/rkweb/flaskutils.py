import http
from copy import deepcopy
from flask import session, request, jsonify, abort as _abort
from webargs import asyncparser
from flask_smorest import Blueprint as Blueprint_

from rkweb.session import AuthSession
from rkweb.base_schema import BaseResponse, SchemaErrorResponse

def get_origin_domain():
    domain = None
    try:
        origin = request.headers.get('Origin')
        if origin:
            parsed = urlparse(origin)
            domain = parsed.netloc
    except:
        pass
    return domain

def respond(code: int=200, data: dict=None, csrf_token=None):
    """
    Create and send response from data.
    This function does not return execution to the caller.

    Args:
        code: HTTP response code
        data: Response JSON data as dictionary
        csrf_token: Optional CSRF token to set in response cookie
    """
    if not data:
        data = {}
    if "status" not in data:
        data["status"] = "Success" if code == 200 else "Failure"
    if "message" not in data:
        data["message"] = "Success"
    ret = jsonify(data)
    ret.status_code = code
    if csrf_token:
        ret.set_cookie(
            key="FXSRF-TOKEN",
            value=csrf_token,
            samesite='Strict',
            secure=True,
            domain=get_origin_domain())

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

def unauthorized(message: str):
    """
    End execution due to missing permission
    Args:
        message: Message about missing authorization
    """
    abort(403, message)

def unauthenticated(message: str):
    """
    End execution due to not being logged in
    Args:
        message: Message about login requirement
    """
    abort(401, message)

def abort_bad_csrf():
    """
    Responds with unauthorized due to invalid CSRF,
    and clears the CSRF token from the cookie
    """
    data = {
        'status': 'Failure',
        'message': 'Invalid CSRF token',
    }
    ret = jsonify(data)
    ret.status_code = 401
    session.clear()
    ret.delete_cookie(key="session")
    ret.delete_cookie(key="fxsession")
    ret.delete_cookie(key="FXSRF-TOKEN")
    _abort(ret)
    assert False

def abort_not_logged_in():
    """
    Responds with a request to clear cookies and not logged in error
    """
    data = {
        'status': 'Failure',
        'message': 'Not logged in',
    }
    ret = jsonify(data)
    ret.status_code = 401
    session.clear()
    ret.delete_cookie(key="session")
    ret.delete_cookie(key="fxsession")
    ret.delete_cookie(key="FXSRF-TOKEN")
    _abort(ret)
    assert False

def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)

def convert_kwargs_to_camel_case(**kwargs):
    new_kwargs = {}
    for key, value in kwargs.items():
        new_key = camelcase(key)
        new_kwargs[new_key] = value
    return new_kwargs

def cameldict(d):
    fin_d = {}
    for key in d:
        value = d[key]
        if isinstance(value, dict):
            fin_d[camelcase(key)] = cameldict(value)
        elif isinstance(value, list):
            fin_l = []
            for subitem in value:
                if isinstance(subitem, dict):
                    fin_l.append(cameldict(subitem))
                else:
                    fin_l.append(subitem)
            fin_d[camelcase(key)] = fin_l
        else:
            fin_d[camelcase(key)] = value
    return fin_d

# Makes flask smorest Blueprint work with async functions
class Blueprint(Blueprint_):
    ARGUMENTS_PARSER = asyncparser.AsyncParser()

    def fxroute(
        self,
        endpoint,
        method,
        schema=None,
        location="json",
        resp_schemas={},
        description=None,
        schema_error_handler=None):

        def param_decorator(func):
            schema_instance = None
            if schema:
                try:
                    schema_instance = schema.schema # lilmodels.Model
                except:
                    schema_instance = schema() # Marshmallow.Schema

            # Process view asynchronously
            async def wrapper(*args, **kwargs):
                kwargs = convert_kwargs_to_camel_case(**kwargs)

                # Get arguments
                args = None
                if schema_instance:
                    if location == "json":
                        if schema_error_handler:
                            try:
                                args = request.get_json(force=True)
                            except:
                                return schema_error_handler(['json'])
                        else:
                            args = request.get_json(force=True)
                    elif location == "query":
                        args = request.args

                    # Convert all snake case to camel case
                    if args:
                        args = cameldict(args)

                    # Validate against schema
                    errors = schema_instance.validate(args)
                    if errors:
                        if schema_error_handler:
                            return schema_error_handler(errors)
                        return abort(422, "Validation error", {"errors": errors})

                # Forward to view
                ret = None
                try:
                    if location == 'query':
                        if args and kwargs.values():
                            ret = await func(args, **kwargs)
                        elif args:
                            ret = await func(args)
                        else:
                            ret = await func({})
                    else:
                        if args and kwargs.values():
                            ret = await func(args, **kwargs)
                        elif kwargs.values():
                            ret = await func(**kwargs)
                        elif args:
                            ret = await func(args)
                        else:
                            ret = await func()
                # Don't keep stateless auth sessions around
                finally:
                    AuthSession.clean_stateless()

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
                    "in": location,
                    "required": True,
                    "schema": schema_instance,
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
                try:
                    resp_schema = resp_schemas[status_code].schema # lilmodels.Model
                except:
                    resp_schema = resp_schemas[status_code]() # Marshmallow.Schema

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

