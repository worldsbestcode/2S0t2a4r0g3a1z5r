"""
@file      kmes/views/crypto.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for crypto operations
"""

from flask import request
from marshmallow import ValidationError

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses


class BaseView(ServerTranslatedView):
    """
    Base View for handling ECC and RSA encryption, decryption, signing and verification
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Crypto")

    def handleResponse(self, response, success_msg):
        not_found_messages = ["Invalid", "RETRIEVING", "UNKNOWN"]
        status, message = response.pop("status", "Y"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(success_msg, response)
        elif status == "P" or "NO PERMISSION" in message:
            return APIResponses.forbidden(message)
        elif any(string in message for string in not_found_messages):
            return APIResponses.not_found(message)
        else:
            return APIResponses.bad_request(message)


class Encrypt(BaseView):
    """
    View for both symmetric and asymmetric encryption with either and RSA or ECC certificate.
    """

    def post(self):
        request_data = request.get_json()
        _type = request_data.pop("type", False)
        operation = _type.capitalize() + "Encrypt" if _type else "Encrypt"

        try:
            try:
                response = self.translate(operation, request_data)
            except NotImplementedError:
                raise ValidationError("Must be one of: ECC, RSA", "type")
        except AttributeError:
            raise ValidationError("Missing field", "type")

        return self.handleResponse(response, "Encryption successful")


class Decrypt(BaseView):
    """
    View for both symmetric and asymmetric decryption with either and RSA or ECC certificate.
    """

    def post(self):
        request_data = request.get_json()
        _type = request_data.pop("type", False)
        operation = _type.capitalize() + "Decrypt" if _type else "Decrypt"

        try:
            try:
                response = self.translate(operation, request_data)
            except NotImplementedError:
                raise ValidationError("Must be one of: ECC, RSA", "type")
        except AttributeError:
            raise ValidationError("Missing field", "type")

        return self.handleResponse(response, "Decryption successful")


class Random(ServerTranslatedView):
    """
    View for generating random bytes
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Crypto")

    def post(self):
        request_data = request.get_json()
        response = self.translate("Random", request_data)
        status, message = response.pop("status", "Y"), response.pop("message", "")

        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P" or "NO PERMISSION" in message:
            return APIResponses.forbidden(message)
        else:
            return APIResponses.bad_request(message)


class Sign(BaseView):
    """
    View for asymmetric data signing with either and RSA or ECC certificate.
    """

    def post(self):
        request_data = request.get_json()
        _type = request_data.pop("type", None)

        try:
            try:
                response = self.translate(_type.capitalize() + "Sign", request_data)
            except NotImplementedError:
                raise ValidationError("Must be one of: ECC, RSA", "type")
        except AttributeError:
            raise ValidationError("Missing field", "type")

        return self.handleResponse(response, "Signing successful")


class Verify(BaseView):
    """
    View for asymmetric signed data verification with either and RSA or ECC certificate.
    """

    def post(self):
        request_data = request.get_json()
        _type = request_data.pop("type", None)

        try:
            try:
                response = self.translate(_type.capitalize() + "Verify", request_data)
            except NotImplementedError:
                raise ValidationError("Must be one of: ECC, RSA", "type")
        except AttributeError:
            raise ValidationError("Missing field", "type")

        message = response.get("message", "")
        response["valid"] = True
        success_msg = None

        if message == "N":
            response["valid"] = False
            success_msg = "Verification failed."

        return self.handleResponse(response, (success_msg or "Verification successful"))
