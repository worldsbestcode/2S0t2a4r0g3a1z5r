"""
@file      regauth/schemas/shared_schemas.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Schemas which are shared between multiple schema modules
"""

from cryptography import x509
from marshmallow import Schema, ValidationError, fields, post_load, validates_schema
from marshmallow.validate import Length

from lib.utils.hapi_excrypt_map import ASN1Types, DefaultRDNs, FixedDNOIDTypes, AsymHashTypes
from lib.utils.string_utils import string_is_hex, DNParser, ParseError
from regauth.regauth_parsers import serialize_extension_oid


class FieldStrOrInt(fields.String):
    """
    Field allows ints or strs, coerces to str before validating
    """

    def deserialize(self, value, *args, **kwargs):
        if isinstance(value, int):
            value = str(value)
        return super(FieldStrOrInt, self).deserialize(value, *args, **kwargs)


class Attributes(Schema):
    attribute = fields.String(required=True)
    value = fields.String(required=True)


class RDN(Schema):
    """
    Represents one Distinguished Name Attribute (multi-typed RDNs not supported)
    """
    id = fields.String(required=True)
    asn1Type = FieldStrOrInt(required=False)
    data = fields.String(required=True, validate=string_is_hex,)

    @post_load
    def check_and_coerce(self, request, **kwargs):
        # Accept OIDs (2.5.4.3) or supported aliases (CN or commonName), but load as OID
        oid = request["id"]
        if all(map(str.isdigit, oid.split("."))):
            pass
        elif oid not in DefaultRDNs:
            choices = ", ".join(sorted(DefaultRDNs.keys()))
            raise ValidationError("Must be a valid OID or one of: {}".format(choices), "id")
        else:
            oid = DefaultRDNs.get(oid)

        # Accept supported ASN.1 types as an int or by name, but load as int
        if "asn1Type" in request:
            asn1Type = request["asn1Type"]
            # Try to coerce string type into int type
            asn1Type = ASN1Types.name_to_value(asn1Type, asn1Type)
        else:
            # Use default of UTF-8 unless this OID has a fixed ASN.1 type
            asn1Type = FixedDNOIDTypes.get(oid, '12')

        # Now validate whether that was a valid ASN1 choice
        if asn1Type != FixedDNOIDTypes.get(oid, asn1Type):
            reason = "OID '{}' cannot have that ASN.1 Type".format(request["id"])
            raise ValidationError(reason, "asn1Type")
        elif asn1Type not in ASN1Types.values:
            choices = ", ".join(ASN1Types.values)
            raise ValidationError("Must be one of: {}.".format(choices), "asn1Type")

        # Success, now save the translated types
        request["id"] = oid
        request["asn1Type"] = str(asn1Type)
        return request


class Subject(fields.Field):
    """
    A full Distinguished Name, either as a list of RDNs (dicts, flat) or a string (CSV)
    """
    def __init__(self, **kwargs):
        self._list_field = fields.Nested(RDN, many=True, validate=Length(1), **kwargs)
        super(Subject, self).__init__(**kwargs)

    def deserialize(self, value, *args, **kwargs):
        # Coerce string type to list type before validating
        if isinstance(value, str):
            value = self.parse_str_format(value)
        return self._list_field.deserialize(value, *args, **kwargs)

    def parse_str_format(self, value):
        parser = DNParser()
        try:
            result = parser.parse(value, oid_field='id', value_field='data')
        except ParseError as e:
            raise ValidationError(str(e))
        return result


class V3Extension(Schema):
    id = fields.String(required=True)
    data = fields.String(required=True, validate=Length(min=2))
    critical = fields.Boolean(missing=False)

    @post_load
    def make_extension_object(self, extension, **kwargs):
        """
        Convert input dict-type object to a cryptography Extension

        Validate the OID is a valid OID or supported alias, and convert to numeric type.
        Validate the data is hex, except for AKI/SKI which are converted to openssl name.
        """
        oid = extension["id"]
        data = extension["data"]
        critical = extension["critical"]

        # Convert OID aliases to their numeric representation "Subject Key Identifier"->"2.5.29.14"
        oid = serialize_extension_oid(oid)
        if not oid:
            raise ValidationError("Invalid Extension OID", "id")
        oid = x509.ObjectIdentifier(oid)

        # Convert special-case extensions to values required by RK "SHA-256"->"SHA256"
        if oid == x509.OID_AUTHORITY_KEY_IDENTIFIER or oid == x509.OID_SUBJECT_KEY_IDENTIFIER:
            data = AsymHashTypes.get(data, None)
            if data is None:
                choices = ', '.join(AsymHashTypes)
                msg = "Key Identifier extensions must name a hash algorithm: {}".format(choices)
                raise ValidationError(msg, "data")
        # All other extensions must be ASN.1-encoded data in hex
        elif not string_is_hex(data):
            raise ValidationError("Must be hex-encoded ASN.1 data", "data")
        else:
            data = data.upper()

        ext = x509.extensions.Extension(oid, critical, data)
        return ext


class ValidityPeriod(Schema):
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    start = fields.DateTime(format=DATE_TIME_FORMAT)
    end = fields.DateTime(format=DATE_TIME_FORMAT)


def require_exactly_one(*args):
    """
    Get a schema validator to check that exactly one field in fields is given
    """
    assert all(isinstance(field_name, str) for field_name in args), "Pass the field name"

    def validator(_, data, **kwargs):
        given = [field for field in args if field in data]
        if len(given) > 1:
            raise ValidationError("Field cannot be combined with {}".format(given[0]), given[1])
        if not given:
            raise ValidationError("At least one field is required", ", ".join(args))

    return validates_schema(validator)
