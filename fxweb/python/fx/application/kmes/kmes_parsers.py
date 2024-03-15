"""
@file      kmes/kmes_parsers.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Parsing functions to supplement Translator request/response mappings
"""

import re
from typing import Dict, List

from cryptography import x509

from lib.utils.hapi_excrypt_map import AsymHashTypes, DaysOfWeek, SecurityUsage
from lib.utils.hapi_parsers import (
    parse_bool,
    parse_nested_csv,
    serialize_bool,
    serialize_nested_csv,
)


def parse_password_policy(csv: str) -> Dict[str, Dict[str, int]]:
    """
    A Password Policy is a csv of several password requirements of the form
    requirementName=requirementMin or requirementName=RequirementMin:requirementMax.
    Example usage:
    parse_password_policy('length=8:10,numeric=2')
    ->
    {'length': {'min':8, 'max':10}, 'numeric':{'min':2}}
    """

    policy = {}
    for field in csv.split(","):
        name, value = field.split("=")
        required_min, *required_max = value.split(":")
        policy[name] = {"min": required_min, **({"max": required_max[0]} if required_max else {})}
    return policy


def serialize_password_policy(csv: Dict[str, Dict[str, int]]) -> str:
    """
    The reverse of parse_password_policy.
    """

    return ",".join(
        [
            "{}={}{}".format(policy, limits["min"], f":{limits['max']}" if "max" in limits else "")
            for policy, limits in csv.items()
        ]
    )


def parse_permission_map(csv: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Permissions in comma separated pairs TYPE:FLAG
    where TYPE is a string referring to a class of permissions (Certs, Keys, etc)
    and FLAG a list of values separated by '|' which represent the permissions for
    the type (add, delete etc)

    Example usage:
    parse_permission_map('Log:|Modify||Export|,User:|Add||Delete||Modify|,Host:|None|')
    ->
    {'Log': {'perms': ['Modify', 'Export]}, 'User': {'perms': ['Add', 'Delete', 'Modify']},
     'Host': {'perms': []}}
    """
    permissions = {}
    for field in csv.split(","):
        if field:
            name, perm_csv = field.split(":")
            perm_list = [perm.strip("|") for perm in perm_csv.split("||")]
            if "None" in perm_list:  # indicates "view only" or this permission class has no flags
                perm_list = []
            permissions[name] = {"perms": perm_list}
    return permissions


def serialize_permissions(permissions: Dict[str, Dict[str, List[str]]]) -> str:
    """
    The reverse of parse_permission_map.
    """

    return ",".join(
        [
            "{}:{}".format(
                perm_type,
                "".join(["|{}|".format(perm) for perm in permissions[perm_type]["perms"]])
                or "|None|",  # "view only" designated by None, e.g., 'PMUser:|None|;'
            )
            for perm_type in permissions.keys()
        ]
    )


def add_names_to_permissions(perm_map, *, type_names=None, flag_names=None):
    """
    Add human readable display names to a Permission Map.
    """

    if type_names:
        for type_name in perm_map:
            type_description = type_names.get(type_name, type_name)
            perm_map[type_name]["display"] = type_description

    if flag_names:
        raise NotImplementedError

    return perm_map


def parse_mo_permissions(csv):
    """
    Parse a Managed Object's permissions CSV into a dict

    @example
        input:
            csv = '{Admin Group,Add},{SomeGroup,Delete}'
        output:
            result = {'Admin Group': 'Add', 'SomeGroup': 'Delete'}
    """
    return dict(pair.strip("{}").split(",") for pair in csv.split("},{") if pair)


def serialize_mo_permissions(perm_map):
    """
    Reverse of parse_mo_permissions
    """
    return ",".join(f"{{{group},{perm}}}" for group, perm in perm_map.items())


def parse_key_types(key_types: str) -> List[Dict]:
    """
    Parse csv of key types (ex: for Issuance Policies)

    @example
        input:
            key_types = 'RSA 2048-4096,ECC 192'
        output:
            result = [
                {'type': 'RSA', 'min': 2048, 'max': 4096},
                {'type': 'ECC', 'min': 192, 'max': 192}
            ]
    """
    result = []
    for entry in key_types.split(","):
        algorithm, _, sizes = entry.partition(" ")
        size_min, _, size_max = sizes.partition("-")
        result.append(
            {
                "type": algorithm,
                "min": int(size_min),
                "max": int(size_max or size_min),
            }
        )
    return result


def serialize_key_types(key_types: List[Dict]) -> str:
    """
    Reverse of parse_key_types
    """
    return ",".join("{type} {min}-{max}".format(**restriction) for restriction in key_types)


def parse_application_features(feature_csv: str):
    output = dict()
    for feature in feature_csv.split(","):
        name, value = feature.split("=")
        output[name] = parse_bool(value) if int(value) < 2 else int(value)

    return output


def parse_firmware_features(feature_csv):
    INT_FEATURES = ["RATE", "PLATFORM"]
    output = dict()
    for feature in feature_csv.split(","):
        for name in INT_FEATURES:
            if feature.startswith(name):
                value = int(feature[len(name) :])
                output[name] = value
                break
        else:
            output[feature] = True

    return output


def serialize_options_to_csv(options: Dict[str, bool]) -> str:
    """
    Serialize a dict of options' status into a CSV of enabled options

    @example
        input:
            options = {'Lowercase': True, 'Uppercase': False, 'Space': True, 'Underscore': False}
        output:
            result = 'Lowercase,Space'
    """
    return ",".join(str(token) for token, enabled in options.items() if enabled)


def parse_date(yyyymmdd: str) -> str:
    yyyy = yyyymmdd[:4]
    mm = yyyymmdd[4:6]
    dd = yyyymmdd[6:8]
    return yyyy + "-" + mm + "-" + dd


def serialize_date_time(date_time):
    return date_time.strftime("%Y%m%d%H%M%S")


def parse_interval(interval: str) -> Dict[str, str]:
    """
    Parse a Time::Interval string (ex: "3 Weeks")
    """
    amount, _, unit = interval.partition(" ")
    return {"amount": int(amount), "unit": unit}


def serialize_subject(obj_list):
    csv_sequence = ("oid", "asn1Type", "value")
    return serialize_nested_csv(obj_list, csv_sequence)


def parse_subject(csv):
    csv_sequence = ("oid", "asn1Type", "value")
    result = parse_nested_csv(csv, csv_sequence)
    *map(lambda d: d.update(asn1Type=int(d["asn1Type"])), result),  # ASN.1 Type was str, make int
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
    name_supplied = oid.replace(" ", "").lower()
    for oid_obj, rfc_name in x509.oid._OID_NAMES.items():
        if name_supplied == rfc_name.lower():
            return oid_obj.dotted_string

    # Wasn't a valid integer OID or any name we know of
    return ""


def serialize_extensions(extensions):
    """
    Parse X509 Extensions object into excrypt acceptable data.

    @param  <cryptography.x509.Extensions>  extensions: an iterable of x509.Extensions
                                                        with an oid, data, and criticality
    @return <str>  Nested csv formated for Excrypt commands

    @example
    * extensions:
        <Extensions([
            <Extension(oid=<ObjectIdentifier(oid=2.5.29.14, name=subjectKeyIdentifier)>,
                            critical=False, value=SHA256)>,
            <Extension(oid=<ObjectIdentifier(oid=2.5.29.18>, critical=True, value=030202C4)>
        ])>

    * output: '{2.5.29.14,SHA256,0},{2.5.29.18,030202C4,1}'

    @Used by:
    * /regauth/regauth_translators.py
        * CreatePKIRequestTranslator
    """

    return ",".join(
        "{%s,%s,%s}"
        % (
            ext.oid.dotted_string,
            ext.value,
            "1" if ext.critical else "0",
        )
        for ext in extensions
    )


def serialize_extensions_list(obj_list):
    csv_sequence = ("oid", "value", "critical")
    obj_list = [dict(d, critical=serialize_bool(d.get("critical"))) for d in obj_list]
    result = serialize_nested_csv(obj_list, csv_sequence)
    return result


def serialize_extension_descriptions(obj_list):
    csv_sequence = ("oid", "mode")
    result = serialize_nested_csv(obj_list, csv_sequence)
    return result


def parse_extensions(csv):
    csv_sequence = ("oid", "value", "critical")
    result = parse_nested_csv(csv, csv_sequence) if csv else []

    hash_oids = [
        x509.OID_SUBJECT_KEY_IDENTIFIER.dotted_string,
        x509.OID_AUTHORITY_KEY_IDENTIFIER.dotted_string,
    ]

    for extension in result:
        critical = extension.get("critical", "0")
        extension["critical"] = parse_bool(critical)

        if extension.get("oid") in hash_oids:
            extension["value"] = AsymHashTypes.get_reverse(extension.get("value"))

    return result


def parse_extension_descriptions(csv):
    """
    Converts Excrypt response to Dictionary
    @Example
        input: "{1.3.6.1.5.5.7.1.1,RESTRICTED},{2.5.29.5,FIXED}"
        output: {"1.3.6.1.5.5.7.1.1":"RESTRICTED", "2.5.29.5":"FIXED"}
    """
    csv_sequence = ("oid", "mode")
    result = {item["oid"]: item["mode"] for item in parse_nested_csv(csv, csv_sequence)}
    return result


def serialize_key_attributes(attribute_list):
    matcher = re.compile(r"[\[\];:,\\'\"]")
    result = []

    for attr in attribute_list:
        invalid_chars = matcher.findall(attr["attribute"] + attr["value"])
        if invalid_chars:
            raise ValueError("Invalid attribute characters: {}".format("".join(invalid_chars)))

        result.append("{}:{}".format(attr["attribute"], attr["value"]))

    return ",".join(result)


def serialize_weekdays(days: List[str]) -> int:
    """
    Converts Weekdays (bit flags, 2^0 = SUNDAY, 2^1 = MONDAY, ..., 2^6 = SATURDAY)
    @Example
        input: ['Sunday', 'Wednesday']
        output: 9
    """
    return sum(DaysOfWeek.get(day, 0) for day in days)


def parse_weekdays(flags: str) -> List[str]:
    """
    Converts Weekdays (bit flags, 2^0 = SUNDAY, 2^1 = MONDAY, ..., 2^6 = SATURDAY)
    @Example
        input: '9'
        output: ['Sunday', 'Wednesday']
    """
    flags = int(flags)
    return [day for day, flag in DaysOfWeek.items() if flag & flags]


def parse_securityusage(flags: str) -> List[str]:
    """
    Converts Security Usage (bit flags, 0x01|0x04 = [Private, Immutable])
    @Example
        input: '0x05'
        output: [Private, Immutable]
    """
    flags = int(flags, 16)
    return [flag for flag, val in SecurityUsage.items() if val and val & flags] or ["None"]


def serialize_securityusage(usage_list: List[str]) -> str:
    return f"{sum(SecurityUsage.get(usage, 0) for usage in usage_list):#04x}"
