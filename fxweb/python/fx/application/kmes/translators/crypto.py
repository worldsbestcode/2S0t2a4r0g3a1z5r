"""
@file      kmes/translators/crypto.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for crypto views
"""

import lib.utils.hapi_excrypt_map as ExcryptMap
import lib.utils.hapi_parsers as parsers
from base.base_translator import BaseTranslator
from kmes.schemas import crypto as schemas
from lib.utils.string_utils import hex_to_b64


class SymmetricEncryptDecrypt(BaseTranslator):
    """
    Base Translator for Symmetric Key Encryption and Decryption

    @used_by
    * /regauth/regauth_translators.py
    """

    VALID_MODES = {
        "decrypt": 0,
        "encrypt": 1,
    }

    def __init__(self, server_interface, mode):
        if mode not in self.VALID_MODES.keys():
            raise ValueError(f"Invalid mode supplied: {mode}")

        fixed_values = {"BF": self.VALID_MODES[mode]}
        request_map = {
            "keyGroup": "KG",
            "keyGroupId": "GI",
            "key": "KN",
            "keyId": "ID",
            "padding": ("BT", parsers.serialize_bool),
            "cipher": ("BJ", ExcryptMap.Cipher.get),
            "data": "BO",
            "dataFormat": ("DF", ExcryptMap.DataFormat.get),
            "mode": "BF",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "KG": "keyGroup",
            "GI": "keyGroupId",
            "KN": "key",
            "ID": "keyId",
            "BT": ("padding", parsers.parse_bool),
            "BJ": ("cipher", ExcryptMap.Cipher.get_reverse),
            "AE": "checksum",
            "BO": "result",
        }

        super().__init__(
            server_interface, "Crypto", "internal_RKED", request_map, response_map, fixed_values
        )


class Decrypt(SymmetricEncryptDecrypt):

    request_schema = schemas.SymmetricDecrypt()

    def __init__(self, server_interface):
        super().__init__(server_interface, "decrypt")


class Encrypt(SymmetricEncryptDecrypt):

    request_schema = schemas.SymmetricEncrypt()

    def __init__(self, server_interface):
        super().__init__(server_interface, "encrypt")


class BaseAsymmetric(BaseTranslator):
    """
    Base Translator for Asymmetric Key Encryption, Decryption, Signing and Verification
    using both ECC and RSA certificates.
    """

    request_schema = schemas.RsaEncryptDecrypt()

    def __init__(self, server_interface, operation):
        request_map = {
            # NA xor (CA and (RT xor AL))
            "pkiTree": "CA",
            "keyId": "KI",
            "key": "NA",
            "hsmStorage": "SH",
            "certId": "ID",
            "certName": "RT",
            "certAlias": "AL",
            "data": "BO",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "BO": "result",
        }

        super().__init__(server_interface, "Crypto", operation, request_map, response_map)


class RsaDecrypt(BaseAsymmetric):
    def __init__(self, server_interface):
        super().__init__(server_interface, "RKRD")
        self.request_map.update({"hashType": ("RG", ExcryptMap.RSAHashTypes.get)})


class RsaEncrypt(BaseAsymmetric):
    def __init__(self, server_interface):
        super().__init__(server_interface, "RKRE")
        self.request_map.update({"hashType": ("RG", ExcryptMap.RSAHashTypes.get)})


class RsaVerify(BaseAsymmetric):
    request_schema = schemas.RsaVerify()

    def __init__(self, server_interface):
        super().__init__(server_interface, "RKRV")
        self.request_map.update(
            {
                "hashType": ("RG", ExcryptMap.RSAVerifyHashTypes.get),
                "digestHash": ("CT", ExcryptMap.RSAVerifyHashTypes.get),
                "padding": ("ZA", ExcryptMap.RSAVerifyPadding.get),
                "saltLength": "ZB",
                "data": "RF",
                "signature": "RH",
            }
        )

    def preprocess_request(self, request):
        request["digestHash"] = "None"

        # Update hash type and digest hash if the data is hashed.
        if request.get("dataIsHashed", False):
            request["digestHash"] = request["hashType"]
            request["hashType"] = "None"

        return request


class EccDecrypt(BaseAsymmetric):
    request_schema = schemas.EccDecrypt()

    def __init__(self, server_interface):
        super().__init__(server_interface, "RKVD")
        self.request_map.update(
            {
                "derivedKeyHashType": ("RG", ExcryptMap.ECIESHashTypes.get),
                "sharedInfo": "AK",
                "iterationCount": "IC",
                "ephemeralPublicKey": "RD",
            }
        )


class EccEncrypt(BaseAsymmetric):
    request_schema = schemas.EccEncrypt()

    def __init__(self, server_interface):
        super().__init__(server_interface, "RKVE")
        self.request_map.update(
            {
                "derivedKeyHashType": ("RG", ExcryptMap.ECIESHashTypes.get),
                "sharedInfo": "AK",
                "iterationCount": "IC",
            }
        )
        self.response_map.update({"RD": "ephemeralPublicKey"})


class EccVerify(BaseAsymmetric):
    request_schema = schemas.EccVerify()

    def __init__(self, server_interface):
        super().__init__(server_interface, "RKVV")
        self.request_map.update(
            {
                "hashType": ("RG", ExcryptMap.ECIESHashTypes.get),
                "digestHash": ("CT", ExcryptMap.ECIESHashTypes.get),
                "data": "RF",
                "signature": "RH",
            }
        )

    def preprocess_request(self, request):
        request["digestHash"] = request["hashType"]

        # Set hash type to none if data is hashed
        if request.get("dataIsHashed", False):
            request["hashType"] = "None"

        return request


class RsaSign(BaseAsymmetric):
    request_schema = schemas.RsaSign()

    def __init__(self, server_interface):
        super().__init__(server_interface, "RKGS")
        self.request_map.update(
            {
                "dataIsHashed": ("HS", parsers.serialize_reverse_bool),
                "hashType": ("RG", ExcryptMap.HashTypes.get),
                "padding": ("ZA", ExcryptMap.PaddingMode.get),
                "saltLength": ("ZB", int),
                "data": "RF",
            }
        )
        self.response_map.update({"RH": "result"})


class EccSign(BaseAsymmetric):
    request_schema = schemas.EccSign()

    def __init__(self, server_interface):
        super().__init__(server_interface, "RKGS")
        self.request_map.update(
            {
                "dataIsHashed": ("HS", parsers.serialize_reverse_bool),
                "hashType": ("RG", ExcryptMap.HashTypes.get),
                "data": "RF",
            }
        )
        self.response_map.update({"RH": "result"})


class Random(BaseTranslator):
    request_schema = schemas.Random()

    def __init__(self, server_interface):
        request_map = {
            "size": "AL",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "AK": ("data", hex_to_b64),
        }

        super().__init__(server_interface, "Crypto", "RAND", request_map, response_map)
