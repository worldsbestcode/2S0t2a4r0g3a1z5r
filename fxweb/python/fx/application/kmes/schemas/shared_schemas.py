"""
@file      kmes/schemas/shared_schemas.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Schemas which are shared between multiple schema modules
"""

import base64
import binascii
import json
from base64 import b64decode

from cryptography import x509
from marshmallow import Schema, ValidationError, fields, post_load, pre_load, validates_schema
from marshmallow.validate import ContainsOnly, Equal, Length, OneOf, Range, Validator

from kmes.kmes_parsers import serialize_extension_oid
from lib.utils.data_structures import FxEnum
from lib.utils.hapi_excrypt_map import (
    ASN1Types,
    AsymHashTypes,
    ClassPermFlag,
    ClassPermMap,
    ClassPermType,
    DefaultRDNs,
    FilterClauseMatch,
    FilterClauseOperator,
    FixedDNOIDTypes,
    ObjectPermType,
)
from lib.utils.hapi_excrypt_map import SecurityUsage as SecurityUsageEnum
from lib.utils.hapi_parsers import flatten_dict
from lib.utils.string_utils import (
    DNParser,
    ParseError,
    from_hex,
    hex_to_uuid,
    is_uuid,
    string_is_b64,
    string_is_hex,
)

USERGROUP_NAME_VALIDATOR = (  # eValDGName from RKValidator::mapValidators in remotekey
    Length(1, 30),
    ContainsOnly("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._ -"),
)

ALIAS_VALIDATOR = (
    Length(1, 80),
    ContainsOnly("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._-"),
)


class UniqueId(fields.String):
    def _deserialize(self, value, *args, **kwargs):
        value = hex_to_uuid(value)
        if value is None:
            raise ValidationError("Not a valid UUID.")
        return super(UniqueId, self)._deserialize(value, *args, **kwargs)


class RequestId(fields.String):
    def __init__(self, *args, **kwargs):
        validator = Length(min=2, max=64)
        kwargs.setdefault("validate", []).append(validator)
        super().__init__(*args, **kwargs)


class StringEnum(fields.String):  # Deprecated
    def __init__(self, options, **kwargs):
        validator = OneOf(choices=options)
        kwargs.setdefault("validate", []).append(validator)
        super().__init__(**kwargs)


class Enum(fields.String):
    """
    An enumeration field. Validates and loads the value into a enum instance.
    """

    default_error_messages = {"no_match": "Must be one of: {choices}."}

    def __init__(self, enum_cls: FxEnum, *, exclude=(), only=(), **kwargs) -> None:
        assert issubclass(enum_cls, FxEnum), "Only supporting FxEnums"
        assert not (exclude and only), "Cannot combine exclude and only"
        assert all(enum_instance in enum_cls for enum_instance in only)
        assert all(enum_instance in enum_cls for enum_instance in exclude)

        self.enum_cls = enum_cls
        self.choices = set(enum for enum in only or enum_cls if enum not in exclude)
        super().__init__(**kwargs)

    def _deserialize(self, value: str, attr, data, **kwargs) -> FxEnum:
        # Note this is called before validators are checked, so validators will see an enum instance
        value = super()._deserialize(value, attr, data, **kwargs)

        enum_instance = None
        try:
            enum_instance = self.enum_cls(value)
        except ValueError:
            pass

        if enum_instance not in self.choices:
            raise self.make_error("no_match", choices=", ".join(sorted(self.choices)))

        return enum_instance


class FieldStrOrInt(fields.String):
    """
    Field allows ints or strs, coerces to str before validating
    """

    def deserialize(self, value, *args, **kwargs):
        if isinstance(value, int):
            value = str(value)
        return super().deserialize(value, *args, **kwargs)


class PermissionsMap(fields.Mapping):
    """
    UserGroup->Permission dict of object permissions (ex: for RKPM)
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("keys", fields.String(validate=USERGROUP_NAME_VALIDATOR))
        kwargs.setdefault("values", fields.String(validate=OneOf(ObjectPermType.names)))
        super().__init__(*args, **kwargs)


class ClassPermissionsMap(fields.Mapping):
    """
    Class->Flag dict of class permissions (ex: creating a user group with RKCW)
    """

    def __init__(self, **kwargs):
        perm_type = fields.String(validate=OneOf(ClassPermType.names))
        perm_flags = fields.Mapping(
            keys=fields.String(validate=Equal("perms")),
            values=fields.List(fields.String(validate=OneOf(ClassPermFlag.names))),
            validate=Length(1),  # Disallow empty dict. View-only indicated by empty list
        )
        super().__init__(
            keys=perm_type,
            values=perm_flags,
            validate=self.validate_perm_options,
            **kwargs,
        )

    _perm_set = set((_type.name, _flag) for _type, _set in ClassPermMap.items() for _flag in _set)

    def validate_perm_options(self, data, **kwargs):
        # Check if supplied perm set is a subset of the maximal perm set
        supplied_set = set(
            (_type, _flag) for _type, _set in data.items() for _flag in _set.get("perms", ())
        )
        invalid = supplied_set - self._perm_set
        if invalid:
            invalid_type, invalid_flag = invalid.pop()
            raise ValidationError(f"'{invalid_type}' cannot have permission '{invalid_flag}'.")


class Attributes(Schema):
    attribute = fields.String(required=True)
    value = fields.String(required=True)


class RDN(Schema):
    """
    Represents one Distinguished Name Attribute (multi-typed RDNs not supported)
    """

    oid = fields.String(required=True)
    asn1Type = FieldStrOrInt(required=False)
    value = fields.String(
        required=True,
        validate=string_is_hex,
    )

    @post_load
    def check_and_coerce(self, request, **kwargs):
        # Accept OIDs (2.5.4.3) or supported aliases (CN or commonName), but load as OID
        oid = request["oid"]
        if all(map(str.isdigit, oid.split("."))):
            pass
        elif oid not in DefaultRDNs:
            choices = ", ".join(sorted(DefaultRDNs.keys()))
            raise ValidationError("Must be a valid OID or one of: {}".format(choices), "oid")
        else:
            oid = DefaultRDNs.get(oid)

        # Accept supported ASN.1 types as an int or by name, but load as int
        if "asn1Type" in request:
            asn1Type = request["asn1Type"]
            # Try to coerce string type into int type
            asn1Type = ASN1Types.name_to_value(asn1Type, asn1Type)
        else:
            # Use default of UTF-8 unless this OID has a fixed ASN.1 type
            asn1Type = FixedDNOIDTypes.get(oid, "12")

        # Now validate whether that was a valid ASN1 choice
        if asn1Type != FixedDNOIDTypes.get(oid, asn1Type):
            reason = "OID '{}' cannot have that ASN.1 Type".format(request["oid"])
            raise ValidationError(reason, "asn1Type")
        elif asn1Type not in ASN1Types.values:
            choices = ", ".join(ASN1Types.names)
            raise ValidationError("Must be one of: {}.".format(choices), "asn1Type")

        # Success, now save the translated types
        request["oid"] = oid
        request["asn1Type"] = str(asn1Type)
        return request


class Subject(fields.Field):
    """
    A full Distinguished Name, either as a list of RDNs (dicts, flat) or a string (CSV)
    """

    def __init__(self, **kwargs):
        self._list_field = fields.Nested(RDN, many=True, validate=Length(1), **kwargs)
        super().__init__(**kwargs)

    def deserialize(self, value, *args, **kwargs):
        # Coerce string type to list type before validating
        if isinstance(value, str):
            value = self.parse_str_format(value)
        return self._list_field.deserialize(value, *args, **kwargs)

    def parse_str_format(self, value):
        parser = DNParser()
        try:
            result = parser.parse(value)
        except ParseError as e:
            raise ValidationError(str(e))
        return result


class V3Extension(Schema):
    oid = fields.String(required=True)
    value = fields.String(required=True, validate=Length(min=2))
    critical = fields.Boolean(missing=False)

    @validates_schema
    def convert_oid_value(self, extension, **kwargs):
        oid = serialize_extension_oid(extension["oid"])
        if not oid:
            raise ValidationError("Invalid Extension OID", "oid")

        # Convert OID aliases to their numeric representation "Subject Key Identifier"->"2.5.29.14"
        extension["oid"] = x509.ObjectIdentifier(oid)

    @post_load
    def make_extension_object(self, extension, **kwargs):
        """
        Convert input dict-type object to a cryptography Extension

        Validate the OID is a valid OID or supported alias, and convert to numeric type.
        Validate the data is hex, except for AKI/SKI which are converted to openssl name.
        """
        data = extension["value"]
        critical = extension["critical"]
        oid = extension["oid"]

        # Convert special-case extensions to values required by RK "SHA-256"->"SHA256"
        if oid == x509.OID_AUTHORITY_KEY_IDENTIFIER or oid == x509.OID_SUBJECT_KEY_IDENTIFIER:
            data = AsymHashTypes.get(data, None)
            if data is None:
                choices = ", ".join(AsymHashTypes)
                msg = "Key Identifier extensions must name a hash algorithm: {}".format(choices)
                raise ValidationError(msg, "value")
        # All other extensions must be ASN.1-encoded data in hex
        elif not string_is_hex(data):
            raise ValidationError("Must be hex-encoded ASN.1 data", "value")
        else:
            data = data.upper()

        ext = x509.extensions.Extension(oid, critical, data)
        return ext


class V3ExtensionSet(fields.List):
    def __init__(self, *args, ext_class=V3Extension, **kwargs):
        super().__init__(fields.Nested(ext_class), *args, **kwargs)

    def _deserialize(self, *args, **kwargs):
        """Override of deserialize to validate extension uniqueness"""
        extensions = super()._deserialize(*args, **kwargs)

        oids = {}
        for idx, extension in enumerate(extensions):
            oids.setdefault(extension.oid.dotted_string, []).append(idx)

        errors = {}
        for oid, indexes in oids.items():
            if len(indexes) <= 1:
                continue

            errors.update(
                {
                    # The normalized message format is key to message list
                    f"{idx}.oid": [f"Duplicate OID '{oid}' provided"]
                    for idx in indexes
                }
            )

        if errors:
            raise ValidationError(errors)

        return extensions


def check_dict_for_duplicates(key, value):
    entries = [entry[key] for entry in value]
    if len(entries) != len(set(entries)):
        raise ValidationError(f"Entry includes duplicate {key} values")


class ValidityPeriod(Schema):
    DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    start = fields.DateTime(format=DATE_TIME_FORMAT)
    end = fields.DateTime(format=DATE_TIME_FORMAT)


class PaginationMixin:
    page = fields.Integer(validate=Range(min=1), missing=1)
    pageCount = fields.Integer(validate=Range(min=1, max=100), missing=50)


class ObjectLookup:
    """
    Schema for generic object list command RKLN

    :param name: the name for the accepted type (ex "KeyGroup")
    :param columns: allowed filter column names dict (ex {"keyName": "name"}), None disables filters
    :param parent: name for simple parent filtering fields, or None to disable
    :param container: name for simple container filtering fields if enabled
    """

    def __new__(cls, name: str, columns: dict, parent: str, container: str, **kwargs):
        attrs = {
            "includeArchived": fields.Boolean(strict=True, missing=False),
            "nameMatch": fields.String(),
            "page": fields.Integer(validate=Range(min=1)),
            "pageCount": fields.Integer(validate=Range(min=1), missing=50),
            "pre_load": cls.pre_load,
        }
        if parent:
            attrs[f"{parent}Id"] = UniqueId()
            attrs[f"{parent}Name"] = fields.String()
            attrs[f"{parent}Alias"] = fields.String()
        if container:
            attrs[f"{container}Id"] = UniqueId()
            attrs[f"{container}Name"] = fields.String()
        if columns:
            context = {}
            context["columns"] = columns
            attrs["filter"] = fields.List(fields.Nested(Filter(context=context)))
        return type(name, (Schema,), attrs)(**kwargs)

    @pre_load
    def pre_load(self, data, **kwargs):
        if "filter" not in data:
            return data

        # Intercept before validation to decode filter
        try:
            json_str = base64.urlsafe_b64decode(data["filter"])
            data["filter"] = json.loads(json_str)
        except binascii.Error:
            raise ValidationError("Invalid base64-encoded JSON object.", "filter")
        return data


class Filter(Schema):
    """
    An individual filter for nesting into a schema
    """

    attribute = fields.Method(None, "check_attribute", required=True)
    clause = fields.Integer(validate=Range(0, 9))
    match = fields.String(required=True, validate=OneOf(FilterClauseMatch.names))
    negate = fields.Boolean(missing=False)
    operator = fields.String(
        validate=OneOf(FilterClauseOperator.names), missing=FilterClauseOperator.AND
    )
    rangeMax = fields.Integer()
    rangeMin = fields.Integer()
    value = FieldStrOrInt(validate=Length(1))

    def __init__(self, *args, **kwargs):
        attribute_field = fields.String()
        self.check_attribute = attribute_field.deserialize
        super().__init__(*args, **kwargs)
        # Initializing validator for "attribute" delayed to get columns
        attribute_field.validators.append(OneOf(self.context["columns"]))

    @validates_schema
    def check_required(self, data, **kwargs):
        if data["match"] == FilterClauseMatch.NUMERIC_RANGE:
            required = ("rangeMin", "rangeMax")
        else:
            required = ("value",)

        for field in required:
            if field not in data:
                raise ValidationError("Missing data for required field.", field)


def require_exactly_one(*args):
    """
    Get a schema validator to check that exactly one field in fields is given
    """
    assert all(isinstance(field_name, str) for field_name in args), "Pass the field name"

    def validator(_, data, **kwargs):
        data = flatten_dict(data)
        given = [field for field in args if field in data]
        if len(given) > 1:
            raise ValidationError(f"Field cannot be combined with {given[0]}", given[1])
        if not given:
            raise ValidationError("At least one field is required", ", ".join(args))

    return validates_schema(validator)


def require_at_least_one(*args):
    """
    Get a schema validator to check that at least one field in fields is given
    """
    assert all(isinstance(field_name, str) for field_name in args), "Pass the field name"

    def validator(_, data, **kwargs):
        data = flatten_dict(data)
        given = [field for field in args if field in data]
        if not given:
            raise ValidationError("At least one field is required", ", ".join(args))

    return validates_schema(validator)


def require_together(*args):
    """
    Get a schema validator to check that either all fields are given or no field is given
    """
    assert all(isinstance(field_name, str) for field_name in args), "Pass the field name"
    args = set(field for field in args)

    def validator(_, data, **kwargs):
        data = flatten_dict(data)
        given = args & data.keys()
        if given and given != args:
            missing = next(iter((args - given)))
            raise ValidationError(f"Field is required if {given.pop()} given", missing)

    return validates_schema(validator)


def require_implication(P, *Q):
    """
    Get validator to enforce that giving P implies giving any Q (can't give P and not give a Q)
    """
    assert isinstance(P, str) and all(isinstance(q, str) for q in Q), "Pass the field name"

    def validator(_, data, **kwargs):
        data = flatten_dict(data)
        if P in data and all(q not in data for q in Q):
            raise ValidationError(f"At least one field is required if {P} given", ", ".join(Q))

    return validates_schema(validator)


def require_not_together(*args):
    """
    Get a schema validator to check that at most one field is given
    """
    assert all(isinstance(field_name, str) for field_name in args), "Pass the field name"

    def validator(_, data, **kwargs):
        data = flatten_dict(data)
        given = [field for field in args if field in data]
        if len(given) > 1:
            raise ValidationError(f"Field cannot be combined with {given[0]}", given[1])

    return validates_schema(validator)


def require_separate(groupa, groupb):
    """
    Get a schema validator to check that no field from groupa is given with a field from groupb
    """
    assert all(isinstance(field_name, str) for field_name in groupa), "Pass the field name"
    assert all(isinstance(field_name, str) for field_name in groupb), "Pass the field name"

    def validator(_, data, **kwargs):
        data = flatten_dict(data)
        givena = [field for field in groupa if field in data]
        givenb = [field for field in groupb if field in data]
        if len(givena) > 0 and len(givenb) > 0:
            raise ValidationError(f"Field cannot be combined with {givena[0]}", givenb[0])

    return validates_schema(validator)


def excrypt_safe_validator(exclude=()):
    """
    Get a schema validator to check that values do not contain reserved characters
    """
    unsafe = ("[", "]", ";", "<", ">")

    def validator(_, data, **kwargs):
        for field, value in flatten_dict(data).items():
            if field in exclude or not isinstance(value, str):
                continue
            for char in unsafe:
                if char in value:
                    raise ValidationError("Field cannot have character '%s'" % char, field)

    return validates_schema(validator)


class Hex(fields.String):
    """
    A string field that only accepts hex values
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(string_is_hex)


class Unique(Validator):
    """
    Validator which succeeds if the values in a sequence are unique.

    @param key: Name of the field that should be unique, if values are dict-like
    """

    _missing = object()

    def __init__(self, key=None):
        self.key = key

    def __call__(self, iterable):
        seen = set()
        for value in iterable:
            if self.key is not None:
                value = value.get(self.key, self._missing)
            if value in seen:
                raise ValidationError(f"Duplicate value supplied: '{value}'")
            if value is not self._missing:
                seen.add(value)
        return iterable


class LdapLoginMixin:
    ldapUsername = fields.String()
    ldapPassword = Hex()

    validate = require_together("ldapUsername", "ldapPassword")


class Base64String(fields.String):
    """
    A string field that only accepts Base64 values
    """

    def _validate(self, value):
        if not string_is_b64(value):
            raise ValidationError("Invalid Base64-encoded value")
        return super(Base64String, self)._validate(value)


class _EncodedStringSchema(Schema):
    encoding = StringEnum(["UTF-8", "Base64", "Hex"], required=True)
    value = fields.String(required=True)

    def load(self, data, *args, **kwargs):
        if isinstance(data, str):
            data = {
                "encoding": "UTF-8",
                "value": data,
            }
        result = super(_EncodedStringSchema, self).load(data, *args, **kwargs)

        encoding = result["encoding"]
        value = result["value"]
        if encoding == "Base64":
            try:
                value = b64decode(value).decode("latin")
            except binascii.Error as e:
                raise ValidationError("Invalid Base64-encoded value: %s" % str(e), "value")
        elif encoding == "Hex":
            try:
                value = from_hex(value)
            except binascii.Error as e:
                raise ValidationError("Invalid hex value: %s" % str(e), "value")

        return value


class EncodedString(fields.Nested):
    """
    A string field that optionally accepts an encoding
    """

    def __init__(self, *args, **kwargs):
        nested = _EncodedStringSchema()
        super().__init__(nested, *args, **kwargs)

    def _deserialize(self, value, *args, **kwargs):
        schema_data = super()._deserialize(value, *args, **kwargs)
        return schema_data


class _NameOrUuidRefSchema(Schema):
    id = UniqueId()
    name = fields.String()

    _validate_given_anything = require_at_least_one("id", "name")

    def load(self, data, *args, **kwargs):
        if isinstance(data, str):
            deduced_field_name = "id" if is_uuid(data) else "name"
            data = {deduced_field_name: data}
        data = super().load(data, *args, **kwargs)
        return data


class NameIdLink(fields.Nested):
    def __init__(self, prefer="id", **kwargs):
        self.prefer = prefer
        nested = _NameOrUuidRefSchema
        super().__init__(nested, **kwargs)

    def _deserialize(self, data, *args, **kwargs):
        data = super()._deserialize(data, *args, **kwargs)
        if self.prefer in data and len(data) > 1:
            data = {self.prefer: data[self.prefer]}
        return data


class SecurityUsage(fields.List):
    def __init__(self, anon_sign=True, **kwargs):
        options = set(SecurityUsageEnum.keys())
        if not anon_sign:
            options.discard("Anonymous Signing")
        validate = [Unique(), self.check_none_alone]
        validate.extend(kwargs.pop("validate", ()))
        super().__init__(cls_or_instance=StringEnum(options), validate=validate, **kwargs)

    def check_none_alone(self, data, **kwargs):
        if len(data) > 1 and "None" in data:
            other_given = data[1 if data[0] == "None" else 0]
            raise ValidationError("'None' cannot be combined with '%s'" % other_given)
        if not data:
            data.append("None")
