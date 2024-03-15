"""
@file      gcse_translators.py
@author    Stephen Jackson(sjackson@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translator for authentication of cse request for gcse_view
"""

from base_translator import BaseTranslator

from kmes.schemas import gcse as schemas


class GCSEWrapTranslator(BaseTranslator):
    """
    JSON to Excrypt map for google client side encryption(cse) wrap and unwrap
    """

    request_schema = schemas.GCSEWrap()

    def __init__(self, server_interface):
        request_map = {
            "authentication": "JW",
            "authorization": "AZ",
            "action": "AC",
            "plaintext": "BO",
            "addAuthData": "AA",
            "reason": "GR",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "BO": "wrappedBlob",
        }

        super().__init__(server_interface, "GoogleCSE", "KACL", request_map, response_map)


class GCSEUnwrapTranslator(BaseTranslator):
    """
    JSON to Excrypt map for google client side encryption(cse) unwrap and unwrap
    """

    request_schema = schemas.GCSEUnwrap()

    def __init__(self, server_interface):
        request_map = {
            "authentication": "JW",
            "authorization": "AZ",
            "action": "AC",
            "wrappedBlob": "BO",
            "addAuthData": "AA",
            "reason": "GR",
            "resource_name": "RN",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "BO": "plaintext",
        }

        super().__init__(server_interface, "GoogleCSE", "KACL", request_map, response_map)
