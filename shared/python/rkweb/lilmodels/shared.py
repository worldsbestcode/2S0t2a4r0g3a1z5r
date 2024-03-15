"""
Copyright Futurex LP
Credits Lilith Neathery
"""

from base64 import b64encode, b64decode
from typing import Optional, Sequence, Set, Union, cast

from marshmallow import ValidationError, fields, validates_schema
from marshmallow.validate import ContainsOnly, Length, OneOf, Range, Regexp

from rkweb.lilmodels.utils import flatten_dict
from rkweb.lilmodels.base import NewType


NAME_VALID_CHARS = ' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._@-'


def require_at_least_one(*args: str):
    """
    Get a schema validator to check that at least one field in fields is given
    """
    assert all(isinstance(field_name, str) for field_name in args), "Pass the field name"

    def validator(_, data, **kwargs):
        data = flatten_dict(data, include_nested_keys=True)
        given = [field for field in args if data.get(field) is not None]
        if not given:
            raise ValidationError("At least one field is required", ", ".join(args))

    return validates_schema(validator)

def require_not_together(*args: str):
    """
    Get a schema validator to check that at most one field is given
    """
    assert all(isinstance(field_name, str) for field_name in args), "Pass the field name"

    def validator(_, data, **kwargs):
        data = flatten_dict(data, include_nested_keys=True)
        given = [field for field in args if data.get(field) is not None]
        if len(given) > 1:
            raise ValidationError(f"Field cannot be combined with {given[0]}", given[1])

    return validates_schema(validator)

def require_implication(P: str, *Q: str):
    """
    Get validator to enforce that giving P implies giving any Q (can't give P and not give a Q)
    """
    assert isinstance(P, str) and all(isinstance(q, str) for q in Q), "Pass the field name"

    def validator(_, data, **kwargs):
        data = flatten_dict(data, include_nested_keys=True)
        if data.get(P) is not None and all(data.get(q) is None for q in Q):
            raise ValidationError(f"At least one field is required if {P} given", ", ".join(Q))

    return validates_schema(validator)


def require_separate(groupa: Union[str, Sequence[str]], groupb: Union[str, Sequence[str]]):
    """
    Get a schema validator to check that no field from groupa is given with a field from groupb
    """
    if isinstance(groupa, str):
        groupa = (groupa,)
    if isinstance(groupb, str):
        groupb = (groupb,)
    assert all(isinstance(field_name, str) for field_name in groupa), "Pass the field name"
    assert all(isinstance(field_name, str) for field_name in groupb), "Pass the field name"

    def validator(_, data, **kwargs):
        data = flatten_dict(data, include_nested_keys=True)
        givena = [field for field in groupa if data.get(field) is not None]
        givenb = [field for field in groupb if data.get(field) is not None]
        if givena and givenb:
            raise ValidationError(f"Field cannot be combined with {givena[0]}", givenb[0])

    return validates_schema(validator)


class OneOfListUnordered(OneOf):
    def __init__(self, choices):
        super().__init__(tuple(tuple(sorted(choice)) for choice in choices))
    def __call__(self, value):
        return super().__call__(tuple(sorted(filter(None, value))))


class __HexField(fields.String):
    def _serialize(self, value: Optional[bytes], *args, **kwargs) -> Optional[str]:
        if value is None:
            return None
        return value.hex().upper()

    def _deserialize(self, value, *args, **kwargs) -> bytes:
        value = super()._deserialize(value, *args, **kwargs)
        try:
            value = bytes.fromhex(value)
        except ValueError:
            raise ValidationError('Invalid Hex value')
        return value


class __B64Field(fields.String):
    def _serialize(self, value, *args, **kwargs) -> Optional[str]:
        if isinstance(value, str):
            value = value.encode('latin')
        if value is not None:
            value = b64encode(value).decode()
        return value

    def _deserialize(self, value, *args, **kwargs) -> bytes:
        value = super()._deserialize(value, *args, **kwargs)
        try:
            value = b64decode(value)
        except ValueError:
            raise ValidationError('Invalid Base64 value')
        return value


class __CanonicalizedUUIDField(fields.UUID):
    def _validated(self, value):
        obj = super()._validated(value)
        return obj and '{' + obj.__str__().upper() + '}'


class __PemOrB64DerField(fields.String):
    """Accept either raw PEM or b64 DER but then naively decode to raw DER bytes"""
    def _serialize(self, *args, **kwargs):
        # should just return PEM for consistency
        return super()._serialize(*args, **kwargs)

    def _deserialize(self, value, *args, **kwargs) -> bytes:
        value = cast(str, super()._deserialize(value, *args, **kwargs))
        value = value.strip()
        if value.startswith('-----BEGIN'):
            value = ''.join(value.splitlines()[1:-1])
        try:
            value = b64decode(value)
        except ValueError:
            raise ValidationError('Invalid Base64 value')
        return value


Hex = NewType('Hex', bytes, field=__HexField)


UUID = NewType('UUID', str, field=__CanonicalizedUUIDField, format='uuid')


Base64Str = NewType('Base64', bytes, field=__B64Field, format='binary')


Permission = NewType('Permission', str)


RoleRef = NewType('Role', str, validate=Regexp(r'^[ a-zA-Z0-9._@-]{3,64}$'))


IdentityRef = NewType('Identity', str, validate=Regexp(r'^[ a-zA-Z0-9._@-]{4,64}$'))


RoleType = NewType('Role Type', str, validate=OneOf(('Administration', 'Application')))


U2fCredential = NewType('U2F Credential Name', str)


MajorKey = NewType('Major Key', str, validate=OneOf(('PMK', 'MFK', 'FTK')))


KeyLabel = NewType('Key Label', str, validate=Regexp(r'^[a-zA-Z0-9_]{0,64}$'))


KeyModifier = NewType('Key Modifier', int, validate=Range(0, 31))


KeySlot = int


KeyChecksum = NewType('Key Checksum Value', str)


PemOrB64Der = NewType('PEM or Base64-Encoded DER', bytes, field=__PemOrB64DerField)
PemField = NewType('PEM', str)


KeyBlockStr = NewType('Key Block', str, validate=Length(min=1))
