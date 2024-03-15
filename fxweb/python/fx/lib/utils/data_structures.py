"""
@file      lib/utils/data_structures.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Defines classes for data structures.
"""

import enum
from types import DynamicClassAttribute
from typing import Callable, Dict, Union


class ExcryptMessage(dict):
    """
    Dict-like implementation of an Excrypt message
    """
    def __init__(self, message: Union[str, bytes, Dict[str, Union[str, bytes, int, None]]] = None, sanitize = True):
        self.sanitize = sanitize
        if message:
            if isinstance(message, str):
                self.update({field[:2]: field[2:] for field in message[1:-1].split(';') if field})
            elif isinstance(message, dict):
                self.update(message)
            elif isinstance(message, bytes):
                self.update(self.parse_bytes(message))

    def parse_bytes(self, msg):
        tmp = {}
        for field in msg[1:-1].split(b';'):
            if field:
                try:
                    key = field[:2].decode()
                    val = field[2:].decode()
                    tmp[key] = val
                except UnicodeDecodeError:
                    key = field[:2].decode('latin')
                    val = field[2:].decode('latin')
                    tmp[key] = val
                except Exception as e:
                    raise e
        return tmp

    def getText(self, sanitized=False) -> str:
        if sanitized:
            return '[' + ''.join(f'{self.sanitized(tag)}{self.sanitized(value)};'
                                 for tag, value in self.items() if value is not None) + ']'
        return '[' + ''.join(f'{tag}{value};' for tag, value in self.items() if value is not None) + ']'

    def getField(self, tag: str, default: str = '') -> str:
        return self.get(tag, default)

    def getFieldAsInt(self, tag: str, default: int = 0) -> int:
        try:
            return int(self[tag])
        except (IndexError, TypeError, ValueError):
            return default

    def getFieldAsBool(self, tag: str, value: str = '1', default: bool = False) -> bool:
        return self.getField(tag) == str(value) if self.hasField(tag) else default

    def getCommand(self):
        return self.get('AO', '')

    def hasField(self, tag: str) -> bool:
        return tag in self

    def setFieldAsString(self, tag: str, value: str):
        self[tag] = str(value)

    hasContext = hasField
    getContext = getField
    setContext = setFieldAsString

    @staticmethod
    def check_invalid(value: str) -> bool:
        """
        Find the first invalid Excrypt character, or None if the value is safe to encode
        """
        for char in str(value):
            if char in ";[]<>":
                return char
        return None


    @staticmethod
    def sanitized(value: Union[str, bytes], table=str.maketrans({c:None for c in '[];'})) -> str:
        if isinstance(value, bytes):
            value = value.decode()
        return value.translate(table)

    @property
    def status(self) -> str:
        return self.getField('AN', self.getField('status', ''))

    @property
    def message(self) -> str:
        return self.getField('BB', self.getField('message', ''))

    @property
    def success(self) -> bool:
        """
        Naively checks a response for success indicators, not compatible with all commands
        """
        return self.status in ('Y', None) and not self.message and self.getCommand() != 'ERRO'

    def __setitem__(self, tag: str, value: Union[str, bytes, int, None]) -> None:
        if value in (None, ...):
            return
        if self.sanitize and isinstance(value, int):
            # also True/False to 1/0
            value = int.__str__(value)
        return super().__setitem__(tag, value)

    __getitem__: Callable[[str], str]

    def copy(self) -> 'ExcryptMessage':
        return type(self)(super().copy())

    def update(self, other, **kwargs) -> None:
        # do what the builtin dict.update does but overridden so we actually call our __setitem__
        # since CPython doesn't as an optimization
        other_items = getattr(other, 'items', None)
        if not other:
            pass
        elif other_items:
            # dict-like interface
            for key, value in other_items():
                self[key] = value
        else:
            # iterable of key-value tuples interface
            for key, value in other:
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value

class ExcryptMessageResponse(ExcryptMessage):
    """
    This is an ExcryptMessage that is being used to build a JSON response
    This will stop booleans/integers from being turned into JSON strings
    """
    def __init__(self, message: Union[str, bytes, Dict[str, Union[str, bytes, int, None]]] = None):
        super().__init__(message, False)

class ImmutableBidict(dict):
    """
    Bijective mapping that acts like a dict but also supports reverse lookups.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reverse = {}
        for k, v in self.items():
            if self.reverse.setdefault(v, k) is not k:
                raise KeyError('Mapping must be one-to-one, but was initialized with duplicate values')

    def __setitem__(self, k, v):
        raise TypeError('ImmutableBidict cannot be modified')

    def get_reverse(self, *args, **kwargs):
        x = self.reverse.get(*args, **kwargs)
        return x


class DisplayEnum(str, enum.Enum):
    """
    Augmented Enum where members have human-readable display names.

    Value converted to string, and assumes one-to-one with name.
    """
    def __new__(cls, value: str, name: str, description: str = None):
        # Build the enum instance. As a str, with str properties
        value = str(value)
        obj = str.__new__(cls, name)
        obj._value_ = value
        obj._name = name  # obj._name_ will be LHS of member declaration
        obj._description = name if description is None else description

        # Precompute maps for lookup, done here to avoid needing metaclass
        cls._values = {**getattr(cls, '_values', {}), value:obj}
        cls._names = {**getattr(cls, '_names', {}), name:obj}

        # Set of enum options for, e.g., schema validators
        cls.values = cls._values.keys()
        cls.names = cls._names.keys()

        return obj

    @DynamicClassAttribute
    def name(self):
        # Property of the enum instance
        return getattr(self, '_name', 'Unknown')

    @DynamicClassAttribute
    def description(self):
        # Property of the enum instance
        return getattr(self, '_description', 'Unknown')

    def __str__(self):
        return self.name

    def __format__(self, spec):
        return self.name

    @classmethod
    def _missing_(cls, value):
        # Enum values are strings so try coercing
        if isinstance(value, str):
            return super()._missing_(value)
        return cls(str(value))

    @classmethod
    def value_to_name(cls, value, default=None):
        """
        Get the name of the enum with the given value

        If missing and default is None, raise ValueError
        """
        obj = cls.enum_from_value(value, default)
        if isinstance(obj, cls):
            return obj.name
        return obj

    @classmethod
    def name_to_value(cls, name, default=None):
        """
        Get the value of the enum with the given name

        If missing and default is None, raise KeyError
        """
        obj = cls.enum_from_name(name, default)
        if isinstance(obj, cls):
            return obj.value
        return obj

    @classmethod
    def enum_from_value(cls, value, default=None):
        """
        Get the enum instance with the given value
        """
        if default is None:
            return cls(value)
        try:
            return cls(value)
        except ValueError:
            pass
        return default

    @classmethod
    def enum_from_name(cls, name, default=None):
        """
        Get the enum instance with the given name
        """
        if default is None:
            return cls._names[name]
        return cls._names.get(name, default)


# Resolve circular dependency - base enum forbids inheritence and FxEnumMeta makes assumptions
# that the created class extends FxEnum, but FxEnumMeta can't reference FxEnum at first because
# it hasn't created it yet. Just setting to None here to be overwritten by FxEnum's classdef
FxEnum = None
FxEnum: enum.Enum  # Just adding a type hint since the suggestions think it's None


class FxEnumMeta(enum.EnumMeta):
    """
    Creates an FxEnum class

    Creates the enum members and sets their conversions
    Dynamically adds conversion methods (to_1, from_1, to_2, from_2)
    Makes API string matching case insensitive
    """
    def __new__(cls, name, bases, namespace):
        # Constructing the derived FxEnum class (not self)

        if FxEnum not in bases:
            assert FxEnum is None, 'Not a derived class'
            # Skip all steps for the base FxEnum class, just make it a regular object
            return type.__new__(cls, name, bases, namespace)

        # Need to remove special attributes (eg column names) since they look like enum definitions to EnumMeta
        reserved_names = ['_columns']
        reserved_name_values = {}
        for attr in reserved_names:
            if attr in namespace:
                reserved_name_values[attr] = namespace.pop(attr)
                namespace._member_names.remove(attr)

        # Now create the whole enumeration, this will iteratively call create_enum_member for each attribute
        # in the namespace that resembles an enum definition, and bind the responses as enum "instances"
        namespace['__new__'] = cls.create_enum_member
        enum_cls = super().__new__(cls, name, bases, namespace)

        # Check if any API strings are the same when lowercased, probably a mistake
        # Enum aliases don't play nice and probably aren't useful for us so for now just forbid them
        aliases = set()
        for enum_instance in enum_cls.__members__.values():
            assert enum_instance.value not in aliases, '({}) Duplicate values or differ only by case ({})'.format(
                enum_cls.__qualname__ + '.' + enum_instance.name, enum_instance.value
            )
            aliases.add(enum_instance.value)

        # Wrap the function that finds enum members to be case-insensitive
        # Note: the function being wrapped is not our FxEnum.__new__ below, EnumMeta has
        #       replaced that with its special lookup function that we are intercepting
        enum_cls.__new__ = cls.make_argument_lowercase_wrapper(enum_cls.__new__)

        # Set a list of bidicts to handle to-from enum-value conversions
        cls.make_conversion_table(enum_cls)
        # Set methods that do the enum-value conversions, with optional column names (instead of to_1, from_3)
        cls.make_converters(enum_cls, **reserved_name_values)

        return enum_cls

    @staticmethod
    def create_enum_member(enum_cls, api_string: str, *conversions: str):
        # Called once for each member definition, response here becomes that enum instance singleton

        # If you want the main representation of the enum to be int you probably don't want this:
        assert isinstance(api_string, str) and api_string, 'Expected str: {} ({})'.format(
            type(api_string).__qualname__, repr(api_string)
        )

        # The api_string passed here becomes the value when jsonified for the HTTP response
        enum_instance = str.__new__(enum_cls, api_string)

        # The _value_ set here becomes the enum value for builtin value->enum lookups, set to
        # lowercase to support case-insensitive lookup. The lookup function will be made to
        # lowercase the input to match this value
        enum_instance._value_ = api_string.lower()

        enum_instance._conversions = conversions

        return enum_instance

    @staticmethod
    def make_conversion_table(enum_cls):
        # Get the number of columns ensuring that at least one enum member is defined:
        try:
            num_conversions = len(next(iter(enum_cls))._conversions)
        except StopIteration:
            raise AssertionError(f'({enum_cls.__qualname__}) No enum members defined')

        table = [{} for _ in range(num_conversions)]
        for enum_instance in enum_cls:
            # Ensure each member definition has the same number of columns:
            assert len(table) == len(enum_instance._conversions), '({}) mismatched # of conversions from previous ({}) vs ({})'.format(
                enum_cls.__qualname__ + '.' + enum_instance._name_, len(enum_instance._conversions), len(table)
            )

            # Will keep member->target in a bidict in the forward direction
            # Ex: get_reverse("3") -> HashTypes("SHA-256")
            for column, value in zip(table, enum_instance._conversions):
                # Skip explicit Nones
                if value is None:
                    continue
                value = str(value)
                # Note that unlike the API strings, conversion values are case sensitive
                assert value not in column.values(), '({}) Duplicate values defined for a conversion ({})'.format(
                    enum_cls.__qualname__ + '.' + enum_instance._name_, value
                )
                column[enum_instance] = str(value)

        table = [ImmutableBidict(column) for column in table]
        enum_cls._conversion_table = table

    @staticmethod
    def make_converters(enum_cls, **kwargs):
        """
        Generates converter methods for each column in the converters table and binds them to the enum class
        """
        column_names = kwargs.get('_columns', None)
        table = enum_cls._conversion_table
        if column_names is None:
            column_names = range(1, len(table) + 1)
        assert len(column_names) == len(table), '({}) Mismatched # columns ({}) vs. column aliases ({})'.format(
            enum_cls.__qualname__, len(table), len(column_names)
        )

        for column_name, bidict in zip(column_names, enum_cls._conversion_table):
            def convert_enum_to_value(enum_instance: FxEnum, accessor=bidict.get) -> str:
                """
                Convert an enum instance to a value in the specified column (column 0 to column "X")
                """
                # The input is not an instance of this enum, which could be caused by double-importing the module:
                assert isinstance(enum_instance, enum_cls), 'No conversion from {} to {}'.format(
                    type(enum_instance).__qualname__, enum_cls.__qualname__
                )
                converted_value = accessor(enum_instance, FxEnum.Unknown.value)
                return converted_value

            def convert_value_to_enum(value: str, accessor=bidict.get_reverse) -> FxEnum:
                """
                Convert a value to an enum instance for the specified conversion (column "X" to column 0)
                """
                if isinstance(value, int):
                    value = str(value)
                enum_instance = accessor(value, FxEnum.Unknown)
                return enum_instance

            setattr(enum_cls, f'to_{column_name}', convert_enum_to_value)
            setattr(enum_cls, f'from_{column_name}', convert_value_to_enum)

    @staticmethod
    def make_argument_lowercase_wrapper(wrapped_method):
        def wrapper(self, value, *args, **kwargs):
            try:
                value = str.lower(value)
            except TypeError:
                pass
            return wrapped_method(self, value, *args, **kwargs)
        return wrapper


class FxEnum(str, enum.Enum, metaclass=FxEnumMeta):
    """
    Base class for an enumeration.

    Attributes defined in a derived class become enum members. Ex:
        class HashTypes(FxEnum):
            SHA_256  = 'SHA-256', 3, 'sha256', 4
            SHA_1    = 'SHA-1',   1, 'sha1',   None
    Yields an enum with two members, HashTypes.SHA_256 and HashTypes.SHA_1

    Enum members can be returned directly to Flask and will be JSONified to the first
    value in the definition tuple ('SHA-256', 'SHA-1'): the "API String" representation.

    Enum members can be converted to and from other string representations given in the
    subsequent columns by methods on the enum class. Ex:
        # Request mentions the API string for SHA_256 (col0 match is not case sensitive):
        http_request = {'hashType': 'Sha-256'}
        request_api_string = http_request['hashType']
        enum = HashTypes(request_api_string)  # <enum: HashType.SHA_256>

        # Translate the enum from column 0 to column 1:
        translated_value = HashTypes.to_1(enum)  # value is '3'
        rkgc_request['RG'] = translated_value

        # A different command uses a different representation (column) in its response tag
        ragx_response = {'HA': 'sha1'}
        raw_value = ragx_response['HA']

        # Translate the value from column 2 to column 0 :
        enum = HashTypes.from_2(raw_value)
        http_response['hashAlgorithm'] = enum  # response will have the string 'SHA-1'

    Aliases for columns can be used instead of the default column index by defining a list
    as the "_column" attribute. Values with None will not be a valid conversion. Invalid
    conversions in the "to_" direction raise an exception. Invalid conversions in the
    "from_" direction return FxEnum.Unknown (JSONified to "Unknown").
    """

    def __str__(self) -> str:
        """
        Get the API-string representation of this enum
        """
        return self[:]

# When conversion fails, falls back to this FxEnum.Unknown object so it still behaves like an enum
FxEnum.Unknown = FxEnum.create_enum_member(FxEnum, 'Unknown')
