"""
Copyright Futurex LP
Credits Lilith Neathery
"""

import collections
from typing import Any, Callable, ClassVar, Dict, Optional, List, Type, TypeVar, Union

import dataclasses
import marshmallow_dataclass
import marshmallow_dataclass.union_field
from marshmallow import Schema as _Schema, ValidationError, fields, validate

from rkweb.lilmodels.fx_decorators import __dataclass_transform__, singledispatchmethod

_T = TypeVar("_T")
_Tjson = TypeVar('_Tjson', Type[str], Type[int], Type[float], Type[Dict[str, Any]], Type[List[Any]],
                 Type[None])


def _init_fn(fields: List[dataclasses.Field], *args, _init_fn=dataclasses._init_fn):
    # Rearrange __init__ param order so that optional fields can be declared before required fields
    # (necessary to derive a class with no defaults from a class with defaults)
    # ~Equivalent to the kw_only argument to dataclasses.dataclass introduced in Python 3.10
    fields.sort(key=lambda f: (f.default, f.default_factory) != (dataclasses.MISSING,)*2)
    return _init_fn(fields, *args)
dataclasses._init_fn = _init_fn


def field(*,
          required: bool = ...,
          example: Any = ...,
          description: str = ...,
          title: str = ...,
          format: str = ...,
          pattern: str = ...,
          validate: Callable[[Any], Any] = ...,
          marshmallow_field: fields.Field = ...,
          dump_only: bool = ...,
          dump_default: _T = ...,
          load_only: bool = ...,
          load_default: _T = ...,
          init: bool = True,
          discriminator: Dict[str, Union[str, Dict[str, type]]] = ...,
          default_factory: Type = ...,
          **kwargs) -> Any:  # return type is dataclasses.Field[_T] which confuses type hints
    """Specify extra properties for a dataclass attribute"""
    # Just wrapping dataclasses.field so annotations suggest actually meaningful arguments

    # These properties will be passed to the marshmallow.Field's __init__
    metadata = {
        'validate': validate,
        'required': required,
        'missing': load_default,
        'dump_only': dump_only,
        'load_only': load_only,
        'marshmallow_field': marshmallow_field,  # Use custom Field instead of from attr's type hint
        # extra metadata nested into the "metadata" to get set by the Field.__init__
        'metadata': {'discriminator': discriminator} if discriminator is not ... else ...,
    }

    # These properties will be shallow copied directly into the OpenAPI schema object in the docs
    metadata.update({
        'example': example,
        'description': description,
        'title': title,
        'format': format,
        'pattern': pattern,  # Don't also give pattern if using marshmallow.validators.Regexp
    })
    # Any other properties passed as kwargs will be available on the Field's "metadata" attribute,
    # and if they match a valid OAS key they will be copied into the OAS spec in the docs
    # All the allowed properties are listed here:
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schemaObject
    # OAS extension keys may be passed if they start with "x_" like "x_securitySchemes"

    metadata = {k: v for k, v in metadata.items() if v is not ...}
    metadata.update(kwargs)
    return dataclasses.field(
        init=init,
        repr=False,
        hash=False,
        compare=True,
        metadata=metadata,
        **({
            'default': dump_default
        } if dump_default is not ... else {}),
        **({
            'default_factory': default_factory
        } if default_factory is not ... else {}),
    )


class Schema(_Schema):
    Model: ClassVar[Type['__Model']]

    def __init__(self, *args, **kwargs):
        self.add_union_strategies()
        super().__init__(*args, **kwargs)
        self._nest_response = self.dump_fields.keys() == {'response'}

    def dump(self, obj, **kwargs):
        if self._nest_response:
            if isinstance(obj, collections.Mapping):
                obj = {'response': obj} if obj and 'response' not in obj else obj
            elif not hasattr(obj, 'response'):
                new_obj = lambda: 0
                new_obj.response = obj
                obj = new_obj

        result = super().dump(obj, **kwargs)
        return result

    def add_union_strategies(self):
        # Promote all the Unions to our derived class to add custom (de)serialization behaviour
        for name, field in self._declared_fields.items():
            if isinstance(field, marshmallow_dataclass.union_field.Union):
                self._declared_fields[name] = UnionField(base_union=field)


class UnionField(marshmallow_dataclass.union_field.Union):
    """Field with custom type deduction strategy for Unions"""
    def __init__(self, base_union: marshmallow_dataclass.union_field.Union, **kwargs):
        # Forward all the arguments given to the base Union.__init__ to the new version:
        for name in ('union_fields', 'default', 'missing', 'required', 'validate', 'metadata',
                     'allow_none', 'load_only', 'dump_only', 'attribute', 'data_key'):
            kwargs.setdefault(name, getattr(base_union, name))
        super().__init__(**kwargs)

        # Fields line up with https://swagger.io/specification/#discriminator-object
        discriminator = self.metadata.get('discriminator', {})
        self.property_name = discriminator.get('propertyName')
        self.mapping = {
            prop_value: field
            for prop_value, discrim_typ in discriminator.get('mapping', {}).items()
            for union_typ, field in self.union_fields if discrim_typ == union_typ
        }

    def _deserialize(self, value: Any, attr: Optional[str], data, **kwargs) -> Any:
        if self.property_name:
            return self.discriminator_deserialize(value, attr, data, **kwargs)
        return self.ordered_deserialize(value, attr, data, **kwargs)

    def _serialize(self, value: Any, attr: str, obj, **kwargs) -> Any:
        if self.property_name:
            return self.discriminator_serialize(value, attr, obj)
        try:
            return super()._serialize(value, attr, obj, **kwargs)
        except TypeError:
            pass
        return self.ordered_serialize(value, attr, obj, **kwargs)

    def discriminator_serialize(self, value: Any, attr: Optional[str], obj, **kwargs) -> Any:
        """Strategy that tries dumping this field based on the value of a different field"""
        response_field_value = getattr(obj, self.property_name)
        mapped_field = self.mapping[response_field_value]
        return mapped_field.serialize(value, attr, obj, **kwargs)

    def ordered_serialize(self, value: Any, attr: Optional[str], obj, **kwargs) -> Any:
        """Strategy that tries dumping each candidate in the union until one has any data at all"""

        for typ, field in self.union_fields:
            result = field.serialize(value, attr, obj, **kwargs)
            if result:
                return result

    def discriminator_deserialize(self, value: Any, attr: Optional[str], data, **kwargs) -> Any:
        """Strategy that tries loading this field based on the value of a different field"""
        try:
            request_field_value = data[self.property_name]
            mapped_field = self.mapping[request_field_value]
        except IndexError:
            raise ValidationError(f'Must specify one of: {", ".join(self.mapping)}',
                                  field_name=self.property_name)
        return mapped_field.deserialize(value, attr, data, **kwargs)

    def ordered_deserialize(self, value: Any, attr: Optional[str], data, **kwargs) -> Any:
        """Strategy that tries loading each candidate in the union until one succeeds"""
        # Skip if we are an Optional[Union[...]]
        if value is None and not self.required:
            return None

        errors: List[ValidationError] = []
        for typ, field in self.union_fields:
            try:
                return field.deserialize(value, attr, data, **kwargs)
            except ValidationError as err:
                errors.append(err)
        raise self.choose_best_match_error(errors)

    def choose_best_match_error(self, errors: List[ValidationError]) -> ValidationError:
        # Arbitrarily choosing to return the error with the fewest fields that don't line up,
        # breaking ties with the error with the fewest mesages total
        return min(errors, key=self.score)

    @singledispatchmethod
    def score(self, _) -> int:
        return 0

    @score.register(str)
    def score_str(self, message: str) -> int:
        if message == 'Unknown field.':
            return 100
        elif message == 'Missing data for required field.':
            return 10
        else:
            return 1

    @score.register(list)
    def score_list(self, error_list: list) -> int:
        return sum(self.score(value) for value in error_list)

    @score.register(dict)
    def score_dict(self, error_dict: dict) -> int:
        return sum(self.score(value) for value in error_dict.values())

    @score.register(ValidationError)
    def score_error(self, error: ValidationError) -> int:
        return self.score(error.messages)


def NewType(
    description: str,
    typ: Type[_T],
    field: Optional[Type[fields.Field]] = None,
    format: Optional[str] = None,
    **kwargs,
) -> Type[_T]:
    """
    Register a custom Field type

    :param name: Name of field type, the OAS description
    :param typ: The primitive type for the dataclass
    :param field: The Marshmallow field used to de/serialize the data, determines OAS type
    :param format: OAS format modifier ex: 'int32', 'date-time', 'email', etc.
    """
    return marshmallow_dataclass.NewType(
        description,
        typ,  # type: ignore
        field,
        format=format,
        **kwargs)


@__dataclass_transform__()
class ModelMeta(type):
    def __new__(cls, name, bases, namespace, base_schema=None, schema_args={}):
        cls_ = type.__new__(cls, name, bases, namespace)  # type: ignore

        # make cls_ into a dataclass
        # TODO: for Python 3.10+, change to pass kw_only=True and remove _init_fn workaround
        cls_ = marshmallow_dataclass.dataclasses.dataclass(cls_)
        # add init=False fields to the Schema unless hidden=True
        field_init = {field: field.init for field in marshmallow_dataclass.dataclasses.fields(cls_)}
        for field, init in field_init.items():
            field.init = init or not field.metadata.get('hidden', False)
        # generate and set cls_.Schema
        marshmallow_dataclass.add_schema(cls_, base_schema=base_schema or Schema)
        # reset inits back to how they were
        for field, init in field_init.items():
            field.init = init

        cls_: Type[Model]
        cls_.Schema.Model = cls_
        cls_.schema = cls_.Schema(**schema_args)

        # forward any overrides from the derived class to the Schema
        for key, value in namespace.items():
            if key.startswith('__'):
                continue
            try:
                setattr(cls_.Schema, key, value.__get__(None, cls_.Schema))
            except AttributeError:
                pass

        return cls_


class Model(metaclass=ModelMeta):
    examples: ClassVar[Dict[str, Dict[Any, Any]]] = {}
    schema: ClassVar[Schema] = Schema()
    Schema: ClassVar[Type[Schema]] = Schema

    def as_dict(self, dirty=True):
        if not dirty:
            try:
                return self._cached_as_dict
            except AttributeError:
                pass
        self._cached_as_dict = marshmallow_dataclass.dataclasses.asdict(self)
        return self._cached_as_dict

    class Meta:
        ordered = True

__Model = Model  # Aliased for type hints


class BaseResponse(Model):
    status: str = 'Success'
    message: str = 'Success'
