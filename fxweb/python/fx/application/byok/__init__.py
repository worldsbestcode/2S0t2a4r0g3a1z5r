import re
import typing

import dataclasses
import marshmallow_dataclass.union_field
import webargs.flaskparser
from apispec.ext.marshmallow import (
    MarshmallowPlugin as __MarshmallowPlugin,
    OpenAPIConverter as __OpenAPIConverter,
)
from flask_smorest import Blueprint as __Blueprint, abort as __abort
from marshmallow import fields

from container_filters import filter_none_recursive

from .translators.base import ByokTranslator
from .byok_interface import ByokServerInterface
from .models.base import BaseResponse, Model, Schema, field
from .views.base import ByokView, translate_with

_T = typing.TypeVar('_T')
_Tview = typing.TypeVar('_Tview', bound=typing.Type[ByokView])


class ByokFlaskParser(webargs.flaskparser.FlaskParser):
    @staticmethod
    def _structure_dict(dict_):
        def structure_dict_pair(r, key, value):
            m = re.match(r"(\w+)\.(.*)", key)
            if m:
                if r.get(m.group(1)) is None:
                    r[m.group(1)] = {}
                structure_dict_pair(r[m.group(1)], m.group(2), value)
            else:
                r[key] = value

        r = {}
        for k, v in dict_.items():
            structure_dict_pair(r, k, v)
        return r

    def load_form(self, req, schema):
        nested_req = lambda: ...
        nested_req.form = self._structure_dict(req.form)
        return super().load_form(nested_req, schema)  # type: ignore


def handle_deserialization_error(error, req, schema, *, error_status_code, error_headers):
    """Called when request data fails to load"""
    raise error  # Let the registered ValidationError handler take care of it


class Blueprint(__Blueprint):

    ARGUMENTS_PARSER = ByokFlaskParser(error_handler=handle_deserialization_error)

    DEFAULT_LOCATION_CONTENT_TYPE_MAPPING = {
        "json": "application/json",
        "form": "application/x-www-form-urlencoded",
        "json_or_form": "application/json",  # <- document optional-form-data as just being json
        "files": "multipart/form-data",
    }

    def __init__(self, *args, **kwargs):
        self._unregistered_views = []
        kwargs.setdefault('import_name', __package__)
        super().__init__(*args, **kwargs)

    @staticmethod
    def prepare_examples(*examples: typing.Optional[typing.Dict[str, dict]],
                         example: typing.Optional[dict] = None,
                         nest=False,
                         success=True) -> typing.Optional[dict]:
        """Combine and format OAS examples"""
        result = {example.get('summary', 'Example'): example} if example else {}
        for ex in examples:
            if ex:
                result.update(ex)

        for ex in result.values():
            status = 'Success' if success else 'Failure'
            if 'value' not in ex:
                value = dict(**ex)
                ex.clear()
                ex['value'] = value
            if nest and 'message' not in ex:
                ex['value'] = {'response': ex['value'], 'status': status, 'message': status}

        return result or None

    @staticmethod
    def _make_doc_response_schema(schema: Schema, registry={}) -> typing.Union[type, Schema]:
        """Document that all responses are wrapped in a "response" dict with a status and message"""
        if schema.dump_fields.keys() == {'status', 'message'}:
            return schema

        # If we've already nested this schema before (i.e., it's used multiple times), we saved a
        # copy of the nested version - return that so we don't generate multiple copies
        try:
            return registry[type(schema)]
        except KeyError:
            pass

        wrapped_schema = {
            'status': fields.String(missing='Success'),
            'message': fields.String(missing='Success'),
        }
        wrapped_schema: typing.Dict[str, typing.Union[fields.Field, type]]

        explicit_response = schema.dump_fields.get('response')
        wrapped_schema['response'] = explicit_response or fields.Nested(schema)

        # Update the name so the $ref to the nested schema doesn't collide with the generated one
        ref_name = type(schema).__name__
        if not explicit_response:
            ref_name += 'Response'

        nested_schema = Schema.from_dict(wrapped_schema, name=ref_name)
        registry[type(schema)] = nested_schema
        return nested_schema

    @staticmethod
    def _prepare_response_content(data: dict) -> dict:
        """Nests successful responses in a "response" dict with a status and message, drops nulls"""
        response = {
            'status': data.pop('status', 'Success'),
            'message': data.pop('message', 'Success'),
        }
        if data:
            response['response'] = data.get('response') or data

        filter_none_recursive(response)
        return response

    def success(self,
                model: typing.Type[Model],
                *,
                description: str = None,
                example: dict = None,
                examples: typing.Dict[str, dict] = None,
                headers: dict = None):
        """Bind a model to a view method with which to serialize the success response"""
        assert model.schema

        combined_examples = self.prepare_examples(examples,
                                                  model.examples,
                                                  example=example,
                                                  nest=True)

        def decorator(func):
            wrapped = super(Blueprint, self).response(
                status_code=200,
                schema=model.schema,
                description=description,
                examples=combined_examples,
                headers=headers,
            )(func)
            wrapped.success_model = model
            return wrapped

        return decorator

    def json(self,
             model: typing.Type[Model],
             *,
             content_type: str = None,
             required: bool = True,
             description: str = None,
             example: dict = None,
             examples: typing.Dict[str, dict] = None,
             allow_formdata: bool = False,
             **kwargs):
        """Bind a model to a view method with which to deserialize the request body"""
        assert model.schema

        combined_examples = self.prepare_examples(examples,
                                                  model.examples,
                                                  example=example,
                                                  nest=False)

        def decorator(func):
            wrapped = super(Blueprint, self).arguments(
                schema=model.schema,
                location='json_or_form' if allow_formdata else 'json',
                content_type=content_type,
                required=required,
                description=description,
                examples=combined_examples,
                **kwargs,
            )(func)
            wrapped.json_model = model
            return wrapped

        return decorator

    def params(self,
             model: typing.Type[Model],
             *,
             required: bool = True,
             description: str = None,
             example: dict = None,
             examples: typing.Dict[str, dict] = None,
             **kwargs):
        """Bind a model to a view method with which to deserialize the request parameters"""
        assert model.schema

        combined_examples = self.prepare_examples(examples,
                                                  model.examples,
                                                  example=example,
                                                  nest=False)

        def decorator(func):
            wrapped = super(Blueprint, self).arguments(
                schema=model.schema,
                location='querystring',
                required=required,
                description=description,
                examples=combined_examples,
                **kwargs,
            )(func)
            wrapped.args_model = model
            return wrapped

        return decorator

    def error(self,
              status_code: int,
              *,
              description: str = None,
              example: dict = None,
              examples: typing.Dict[str, dict] = None,
              headers: dict = None):
        """Annotate an error response"""
        combined_examples = self.prepare_examples(examples,
                                                  example=example,
                                                  nest=True,
                                                  success=False)

        return self.alt_response(status_code,
                                 BaseResponse.Schema,
                                 description=description,
                                 examples=combined_examples,
                                 headers=headers)

    def route(self, rule: str, *, document: bool = True):
        """Register a URI route to a MethodView"""
        def wrap(view_cls: _Tview) -> _Tview:
            # Prevent duplicates by renaming the endpoint in case of collision
            name = view_cls.__name__
            count = self._endpoints.count(name)
            self._endpoints.append(name)
            name += f'_{count}' if count else ''
            self._unregistered_views.append((rule, name, view_cls))

            if document:
                self._store_endpoint_docs(name, view_cls, None)
            return view_cls

        return wrap

    def register_views(self, *args, **kwargs):
        """Register views to this blueprint, args will be forwarded to their __init__"""
        for rule, name, view_cls in self._unregistered_views:
            as_view_fn = view_cls.as_view(name, *args, **kwargs)
            self.add_url_rule(rule, name, as_view_fn)
        self._unregistered_views.clear()


def abort(status_code: int, message: str, *, errors: dict = None, headers: dict = None) -> typing.NoReturn:
    __abort(status_code, message=message, errors=errors, headers=headers)
    # Unreachable at runtime but static analyzer can't figure that out:
    assert False


class _ByokConverter(__OpenAPIConverter):
    def nested2properties(self, field, ret):
        # hook into this to add oneOf for Union types
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


class ByokMarshmallowPlugin(__MarshmallowPlugin):
    Converter = _ByokConverter
