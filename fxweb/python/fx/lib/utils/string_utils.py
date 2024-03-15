"""
@file      string_utils.py
@author    David Neathery (dneathery@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Utilities for string operations
"""

import re
import json
import base64
import string
import binascii
from typing import Union
from uuid import UUID


def parse_boolean(value: Union[str, bytes, bool, int]) -> bool:
    """
    Coerce type to bool (ex: str 'FALSE' -> bool False)
    """
    if isinstance(value, int):
        return value != 0
    if not value:
        return False
    return value.lower() not in ('0', 'false', b'0', b'false')


def sentence_case(message):
    """
    Convert a string to sentence case. Like this docstring.
    """
    boundaries = '.!?\n'
    if message:
        message = re.sub(
            fr'(^|[{boundaries}]\s*)([a-z])',
            lambda match: match.group().upper(),
            message.lower()
        )
    return message


def string_is_b64(message):
    result = True

    try:
        base64.b64decode(message, validate=True)
    except binascii.Error:
        result = False

    return result


def string_is_hex(message):
    """
    Check whether a string is valid hex (excluding 0x flag)
    """
    return len(message) % 2 == 0 and re.search(r'[^0-9a-fA-F]', message) is None


def to_hex(data):
    if isinstance(data, str):
        data = data.encode('latin')
    return binascii.hexlify(data).decode().upper()


def from_hex(data):
    if isinstance(data, str):
        data = data.encode()
    return binascii.unhexlify(data).decode('latin')


allowed_jwt_chars = set(string.ascii_letters + string.digits + '-_.')
def string_is_jwt(token):
    """
    Check if string resembles a well-formed JWT.
    """
    # if re.search(r'[^A-Za-z0-9-_.]', token) is not None:
    if any(ch not in allowed_jwt_chars for ch in token):
        return False # especially do not allow reserved Excrypt characters

    try:
        header, payload, signature = token.split('.')

        # Padding '='s must be removed from JWTs. Only adding them so base64 doesn't complain:
        header = base64.urlsafe_b64decode(header + '===')
        header = json.loads(header)
        # Cannot check the typ header because it is not required to be "JWT" by RFC 7519

        payload = base64.urlsafe_b64decode(payload + '===')
        payload = json.loads(payload)

        signature = base64.urlsafe_b64decode(signature + '===')
    except (ValueError, TypeError, AttributeError):
        return False
        # raise

    return True


allowed_api_key_chars = set(string.ascii_letters + string.digits + '-_')
def string_is_api_key(token):
    """
    Check if string resembles a well-formed API Key.
    """
    if len(token) < 78 or any(ch not in allowed_api_key_chars for ch in token):
        return False # especially do not allow reserved Excrypt characters

    return True


def hex_to_b64(hex: str) -> str:
    """
    Convert a hex-encoded string to a base64-encoded string.
    """
    text = binascii.unhexlify(hex)
    return base64.b64encode(text).decode()


def b64_to_hex(b64: str) -> str:
    """
    Convert a base64-encoded string to a hex-encoded string.
    """
    text = base64.b64decode(b64, validate=True)
    return binascii.hexlify(text).decode()


def is_hex_digit(val):
    return val and val in '0123456789ABCDEFabcdef'


class DNParser(object):
    """
    Parse a string according to RFC 4514 (and RFC 1779)

    The result is flat for use in ASGC (not multiple attributes per RDN per DN)
    """

    def parse(self, dn_string, oid_field='oid', value_field='value'):
        # Match a sequence of RDNs, each a sequence of key-value pairs
        self.full_string = dn_string
        self.pos = 0
        result = []
        while self.peek():
            if self.peek() in ',;+':
                self.advance(1)
                continue
            key, value = self.match_attribute()
            result.append(
                {
                    oid_field: key,
                    value_field: value,
                }
            )
        return result

    def match_attribute(self):
        self.skip_whitespace()
        key = self.match_key()
        if not key:
            raise self.error('Expected attributeType')
        self.skip_whitespace()
        if self.peek() == '=':
            self.advance(1)
        else:
            raise self.error('Expected attributeValue')
        self.skip_whitespace()
        value = self.match_string()
        self.skip_whitespace()
        return (key, value)

    def match_key(self):
        # <key> ::= 1*( <keychar> ) | "OID." <oid> | "oid." <oid>
        # <keychar> ::= letters, numbers, and space
        key = ''
        if self.is_next('oid.') or self.is_next('OID.'):
            self.advance(4)
            key = self.match_oid()
            if not key:
                raise self.error('Expected oid')
        else:
            while self.peek().isalnum() or self.peek().isspace() or self.peek() == '.':
                key += self.get()
        key = key.strip()
        return key

    def match_oid(self):
        value = ''
        while (self.peek() == '.' or self.peek().isdigit()):
            value += self.get()
        return value

    def match_string(self):
        # <string> ::= *( <stringchar> | <pair> )
        #             | '"' *( <stringchar> | <special> | <pair> ) '"'
        #             | "#" <hex>
        # <special> ::= "," | "=" | <CR> | "+" | "<" |  ">"
        #             | "#" | ";"
        # <pair> ::= "\" ( <special> | "\" | '"')
        # <stringchar> ::= any character except <special> or "\" or '"'

        # If already in hex, just use that
        if self.peek() == '#':
            self.advance(1)
            return self.match_hex()

        result = ''
        delimited = self.is_next('"')
        if delimited:
            self.advance(1)
            special = '"'
        else:
            special = ',=\n\r+<>#;'

        # consume up until delimiter, checking for \ escaped
        # converts values into hex, except for already-escaped hex
        while self.peek() and self.peek() not in special:
            ch = self.get()
            if ch != '\\':
                result += binascii.hexlify(ch.encode()).decode()
                continue
            # escaped, get the escaped value:
            ch = self.get()
            if not ch:
                raise self.error('Expected escaped character')
            # escaped reserved character:
            elif ch in special or ch in '"\\':
                result += binascii.hexlify(ch.encode()).decode()
            # escaped unicode code point in hex, get both :
            elif is_hex_digit(ch) and is_hex_digit(self.peek()):
                result += ch + self.get()
            else:
                raise self.error('Expected escapable character or code point')

        # consume trailing quote
        if delimited and not self.is_next('"'):
            raise self.error('Expected closing quote')
        elif delimited:
            self.advance(1)

        return result

    def match_hex(self):
        result = ''
        while is_hex_digit(self.peek()):
            result += self.get()
        if len(result) % 2 != 0:
            raise self.error('Expected hex digit')
        return result

    def peek(self):
        if self.pos < len(self.full_string):
            return self.full_string[self.pos]
        return ''

    def get(self):
        ch = self.peek()
        self.advance(1)
        return ch

    def advance(self, value):
        self.pos += value

    def is_next(self, value):
        return self.full_string[self.pos:].startswith(value)

    def skip_whitespace(self):
        while self.peek().isspace():
            self.advance(1)

    def error(self, reason):
        return ParseError(reason, self.pos)


class ParseError(Exception):
    def __init__(self, reason, position):
        self.reason = reason
        self.position = position

    def __str__(self):
        return self.reason + ' at position ' + str(self.position)


def is_uuid(val):
    """
    Check if string is a UUID
    """
    is_uuid = False
    try:
        UUID(val)
        is_uuid = True
    except (TypeError, ValueError):
        pass

    return is_uuid


def hex_to_uuid(val):
    """
    Convert a hex UUID to string UUID (braces and hyphens included).
    """
    result = None
    try:
        result = UUID(val)
        result = "{" + str(result).upper() + "}"
    except (TypeError, ValueError):
        pass
    return result


def hex_der_to_pem(hex_der: str, label: str):
    """
    Convert a hex-encoded DER string to RFC-7468 format with label
    """
    # https://datatracker.ietf.org/doc/html/rfc7468#section-3
    body = hex_to_b64(hex_der)
    body_lines = '\n'.join(
        body[line_start:line_end]
        for line_start, line_end in zip(range(0, len(body), 64), range(64, len(body)+64, 64))
    ).rstrip('\n')
    pem = f"-----BEGIN {label}-----\n{body_lines}\n-----END {label}-----\n"
    return pem
