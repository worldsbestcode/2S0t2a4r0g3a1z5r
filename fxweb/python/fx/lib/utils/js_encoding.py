"""
@file      js_encoding.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
 Conversion between js encodeURI and python urllib.quote
"""
import urllib.parse
import json

SAFE_URI = '~@#$&()*!+=:;,.?/\''
SAFE_URI_COMPONENT = '~()*!.\''


def encode_uri(value):
    """Converts the value into a uri string
    Args:
        value: The string to convert

    Returns: A quoted string
    """
    return urllib.parse.quote(value.encode('ascii'), safe=SAFE_URI)


def encode_uri_component(value):
    """Converts the value into a uri component string
    Args:
        value: The string to convert

    Returns: A quoted string
    """
    return urllib.parse.quote(value.encode('ascii'), safe=SAFE_URI_COMPONENT)


def json_uri(obj):
    """Converts the value into a json then into a uri string
    Args:
        value: The string to convert

    Returns: A quoted string
    """
    return encode_uri(json.dumps(obj))


def json_uri_component(obj):
    """Converts the value into json then into a uri component string
    Args:
        value: The string to convert

    Returns: A quoted string
    """
    return encode_uri_component(json.dumps(obj))
