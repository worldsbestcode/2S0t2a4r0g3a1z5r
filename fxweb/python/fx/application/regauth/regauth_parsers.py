"""
@file      regauth/regauth_parsers.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Parsing functions to supplement Translator request/response mappings
"""
import re

from cryptography import x509

from lib.utils.hapi_excrypt_map import AsymHashTypes
from lib.utils.hapi_parsers import parse_bool, parse_nested_csv, serialize_nested_csv


def parse_date(yyyymmdd):
    yyyy = yyyymmdd[ :4]
    mm   = yyyymmdd[4:6]
    dd   = yyyymmdd[6:8]
    return yyyy + '-' + mm + '-' + dd

def serialize_date_time(date_time):
    return date_time.strftime('%Y%m%d%H%M%S')

def serialize_subject(obj_list):
    csv_sequence = ('id', 'asn1Type', 'data')
    return serialize_nested_csv(obj_list, csv_sequence)

def parse_subject(csv):
    csv_sequence = ('id', 'asn1Type', 'data')
    result = parse_nested_csv(csv, csv_sequence)
    *map(lambda d: d.update(asn1Type=int(d['asn1Type'])), result),  # ASN.1 Type was str, make int
    return result

def serialize_extension_oid(oid):
    """
    Attempts to serialize provided OID by using the cryptography.x509 module.
    Returns an empty string if module cannot serialize provided OID.

    @param  <str>   oid: String, or dotted string, representation of Extension OID (RFC 5280)
    @return <str>   Dotted string representation of OID if valid. Empty string if invalid.

    @Used By:
    * serialize_extensions()
    * /regauth/schemas/shared_schemas.py
        * V3Extension
    """

    # Check if they gave integer OID
    try:
        oid_obj = x509.oid.ObjectIdentifier(oid)
        return oid_obj.dotted_string
    except ValueError:
        pass

    # They may be trying to pass the name, do a case-insensitive search
    name_supplied = oid.replace(' ', '').lower()
    for oid_obj, rfc_name in x509.oid._OID_NAMES.items():
        if name_supplied == rfc_name.lower():
            return oid_obj.dotted_string

    # Wasn't a valid integer OID or any name we know of
    return ''

def serialize_extensions(extensions):
    """
    Parse X509 Extensions object into excrypt acceptable data.

    @param  <cryptography.x509.Extensions>  extensions: an iterable of x509.Extensions with an oid, data, and criticality
    @return <str>  Nested csv formated for Excrypt commands

    @example
    * extensions:
        <Extensions([
            <Extension(oid=<ObjectIdentifier(oid=2.5.29.14, name=subjectKeyIdentifier)>, critical=False, value=SHA256)>,
            <Extension(oid=<ObjectIdentifier(oid=2.5.29.18>, critical=True, value=030202C4)>
        ])>

    * output: '{2.5.29.14,SHA256,0},{2.5.29.18,030202C4,1}'

    @Used by:
    * /regauth/regauth_translators.py
        * CreatePKIRequestTranslator
    """

    return ','.join(
        "{%s,%s,%s}" % (
            ext.oid.dotted_string,
            ext.value,
            "1" if ext.critical else "0",
        ) for ext in extensions)

def parse_extensions(csv):
    csv_sequence = ('id', 'data', 'critical')
    result = parse_nested_csv(csv, csv_sequence) if csv else []

    hash_oids = [
        x509.OID_SUBJECT_KEY_IDENTIFIER.dotted_string,
        x509.OID_AUTHORITY_KEY_IDENTIFIER.dotted_string,
    ]

    for extension in result:
        critical = extension.get('critical', '0')
        extension['critical'] = parse_bool(critical)

        if extension.get('oid') in hash_oids:
            extension['value'] = AsymHashTypes.get_reverse(extension.get('value'))

    return result

def serialize_key_attributes(attribute_list):
    matcher = re.compile(r"[\[\];:,\\'\"]")
    result = []

    for attr in attribute_list:
        invalid_chars = matcher.findall(attr['attribute'] + attr['value'])
        if invalid_chars:
            raise ValueError('Invalid attribute characters: {}'.format(''.join(invalid_chars)))

        result.append('{}:{}'.format(attr['attribute'], attr['value']))

    return ','.join(result)
