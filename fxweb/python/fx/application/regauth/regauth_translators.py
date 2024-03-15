"""
@file      regauth_translators.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
All the RegAuth translators that the MethodViews look up
"""
from binascii import unhexlify

import re
import sys

from marshmallow import EXCLUDE

import regauth.schemas as schemas
import lib.utils.hapi_excrypt_map as ExcryptMap
import lib.utils.hapi_parsers as parsers
from base_translator import BaseTranslator
from lib.utils.container_filters import coalesce_dict
from rk_host_application.rk_host_exceptions import FailedRAVD

from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding

from . import (
    regauth_parsers,
)


def map_translators():
    return {
        'Approvals': {
            'CreatePKI': CreatePKIRequestTranslator,
        },
        'Certificates': {
            'RetrievePKI': RetrievePKIRequestTranslator,
            'List': ListCertificatesTranslator,
            'Export': ExportCertificateTranslator,
            'ImportPkcs12': ImportCertificateTranslator,
            'EncryptRSA': EncryptRSATranslator,
            'EncryptECIES': EncryptECIESTranslator,
            'DecryptRSA': DecryptRSATranslator,
            'DecryptECIES': DecryptECIESTranslator,
            'GenerateSignature': GenerateSignatureTranslator,
            'VerifyRSA': VerifyRSATranslator,
            'VerifyECC': VerifyECCTranslator,
        },
        'DNProfiles': {
            'Retrieve': RetrieveDNProfileTranslator,
        },
        'Keys': {
            'CreateRandomKey': CreateRandomKeyTranslator,
            'CreateRandomProtectedKey': CreateRandomProtectedKeyTranslator,
            'ExportSymmetric': ExportSymmetricKeyTranslator,
            'ExportSymmetricProtected': ExportSymmetricProtectedKeyTranslator,
            'ImportProtectedKey': ImportProtectedKeyTranslator,
            'RetrieveSymmetricProtected': RetrieveSymmetricProtectedKeyGroupTranslator,
            'GeneralEncryption': GeneralEncryptionTranslator,
        },
        'System': {
            'EchoInfo': EchoTranslator,
        },
    }


class EchoTranslator(BaseTranslator):
    """
    JSON to Excrypt map for retrieving system information
    """

    request_schema = schemas.Echo(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'message': 'ST',
        }
        response_map = {
            'SR': 'customMessage',
            'BC': 'revision',
            'OS': 'version',
        }

        super().__init__(server_interface, 'System', 'ECHO', request_map, response_map)


class CreatePKIRequestTranslator(BaseTranslator):
    """
    JSON to Excrypt map for creating a PKI Request
    """

    request_schema = schemas.CreatePKIRequest(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'pkiTree': 'CA',
            'signingCert': 'RT',
            'requestName': 'NA',
            'hashType': ('HA', ExcryptMap.AsymHashTypes.get),
            'approvalGroup': 'GN',
            'ldapUsername': 'LU',
            'ldapPassword': 'LP',
            'commonNameAsSan': ('NS', parsers.serialize_bool),
            'renewalCheck': ('RE', parsers.serialize_bool),
            'subjectAltNames': ('AS', parsers.serialize_csv),
            'pkiOptions.extensionProfile': 'EN',
            'pkiOptions.v3Extensions': ('EX', regauth_parsers.serialize_extensions),
            'pkiOptions.keyType': 'KT',
            'pkiOptions.randomPassphrase': ('MP', parsers.serialize_bool),
            'pkiOptions.passphrase': 'PW',
            'pkiOptions.subject': ('SN', regauth_parsers.serialize_subject),
            'pkiOptions.certExpiration': ('AF', regauth_parsers.serialize_date_time),
            'pkiOptions.savePkiKey': ('SK', parsers.serialize_bool),
            # 'pkiOptions.dnProfile' : makes RAVD call
            # 'pkiOptions.dnProfileId' : alternative, makes RAVD call
            # 'pkiOptions.exportPkcs12': makes RASX call
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'ID': 'requestId',
            'AP': ('approvalsRemaining', int),
        }

        super().__init__(server_interface, 'Approvals', 'RAUP', request_map, response_map)

    def preprocess_request(self, request):
        options = request.get('pkiOptions', {})
        if not options:
            return request

        # If they supplied a DN profile, get that profile with RADV to set any missing RDNs
        subject_default = []
        if 'dnProfileId' in options:
            subject_default = self.get_dn_profile(options['dnProfileId'], uuid=True)
        elif 'dnProfile' in options:
            subject_default = self.get_dn_profile(options['dnProfile'], uuid=False)

        # If any OIDs are in the profile and not given in the subject, add them from the profile.
        # Explicitly supplied values replace profile's values. Preserve order if OID is the same.
        if subject_default:
            explicit_subject = options.setdefault('subject', [])
            explicit_oids = set(rdn['id'] for rdn in explicit_subject)
            implicit_subject = [rdn for rdn in subject_default if rdn['id'] not in explicit_oids]
            request['pkiOptions']['subject'].extend(implicit_subject)

        return request

    def get_dn_profile(self, data, uuid):
        request = {'id': data} if uuid else {'name': data}
        response = RetrieveDNProfileTranslator(self.server_interface).translate(request)
        status = response.get('status', 'N')
        if status != 'Y':
            raise FailedRAVD(status, response.get('message', ''))
        return response.get('subject', [])

    def finalize_response(self, response):
        success = response.get('status', 'N') == 'Y'

        if success:
            request_id = self.raw_response.get('ID')

            # Return certId if savePkiKey was requested
            save_pki_key = self.raw_request.get('pkiOptions', {}).get('savePkiKey', False)

            if save_pki_key and request_id:
                response['certId'] = request_id

            # Export and return PKCS #12 if pkcs12 was requested, and 0 approvals remain
            export_pkcs12 = self.raw_request.get('pkiOptions', {}).get('exportPkcs12', False)
            remaining_approvals = response.get('approvalsRemaining')

            if export_pkcs12 and int(remaining_approvals) == 0:
                # Retrieve user passphrase if supplied. Otherwise use generated passphrase
                passphrase = self.raw_request['pkiOptions'].get('passphrase', '')
                passphrase = self.raw_response.get('PW', passphrase)

                rasx_request = {
                    'ID': request_id,
                }
                if passphrase:
                    rasx_request['PW'] = passphrase
                rasx_response = self.server_interface.send_command('Approvals', 'RASX',
                                                                   rasx_request)

                # Add PKCS #12 to response
                pkcs12 = rasx_response.get('PK', '')
                rasx_status = rasx_response.get('AN', 'N')

                if rasx_status == 'Y' and pkcs12:
                    response['pkcs12'] = pkcs12
                else:
                    response['status'] = rasx_status
                    response['message'] = 'Failed to export: {}' \
                        .format(rasx_response.get('BB', 'No PKCS #12 in response'))

        return response


class RetrievePKIRequestTranslator(BaseTranslator):
    """
    JSON to Excrypt map for retrieving a PKI Request
    """

    request_schema = schemas.RetrievePKIRequest(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'requestId': 'ID',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'NA': 'requestName',
            'ST': 'signingStatus',
            'CN': 'signingCert',
            'CP': ('numApprovals', int),
            'NP': ('approvalsRequired', int),
            'AP': ('approvalsRemaining', int),
            'HA': 'hashType',
            'EN': 'pkiOptions.extensionProfile',
            'AF': ('pkiOptions.certExpiration', regauth_parsers.parse_date),
            'SN': ('pkiOptions.subject', regauth_parsers.parse_subject),
            'EX': ('pkiOptions.v3Extensions', regauth_parsers.parse_extensions),
            'KT': 'pkiOptions.keyType',
            'CE': 'pkiOptions.signedCert',
            'PK': 'pkiOptions.pkcs12',
        }

        super().__init__(server_interface, 'Certificates', 'RAGP', request_map, response_map)

    def finalize_response(self, response):
        if self.raw_request["_format"] == "PEM" and response.get("pkiOptions", {}).get("signedCert"):
            try:
                cert_data = x509.load_der_x509_certificate(unhexlify(response["pkiOptions"]["signedCert"].encode()))
                response["pkiOptions"]["signedCert"] = cert_data.public_bytes(Encoding.PEM).decode("utf-8")
            except ValueError:
                response["message"] = "Failed to parse certificate data."
        return response


class ExportCertificateTranslator(BaseTranslator):
    """
    JSON to Excrypt map for exporting a Certificate
    """

    request_schema = schemas.ExportCertificate(unknown=EXCLUDE)

    def __init__(self, server_interface):
        fixed_values = {
            'EF': '0',
        }
        request_map = {
            'pkiTree': 'CA',
            'certCommonName': 'RT',
            'certAlias': 'AL',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'RV': 'certData',
        }

        super().__init__(server_interface, 'Certificates', 'RKRK', request_map, response_map, fixed_values)

    def finalize_response(self, response):
        # Convert hex-encoded DER to PEM
        if 'certData' in response:
            _format = self.raw_request["_format"] 
            if _format != "JSON":
                extension = "der"
                cert_data = unhexlify(response['certData'].encode())

                if _format != "DER":
                    extension = "pem"
                    try:
                        _cert_data = x509.load_der_x509_certificate(cert_data)
                        cert_data = _cert_data.public_bytes(Encoding.PEM).decode("utf-8")
                    except ValueError:
                        response["message"] = "Failed to parse certificate data."
                
                response['certData']  = cert_data
                # Default filename to X509_Certificate
                # Update filename is filename, certAlias, or certCommonName is provided
                filename = coalesce_dict(self.raw_request, ['filename', 'certAlias', 'certCommonName'], 'X509_Certificate')

                response['filename'] = filename + "." + extension

        return response


class ImportCertificateTranslator(BaseTranslator):
    """
    JSON to Excrypt map for importing a Certificate from a PKCS12 file
    """
    request_schema = schemas.ImportPkcs12Certificate(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'pkiTree': 'CA',
            'parent': 'RT',
            'parentAlias': 'AL',
            'passphrase': 'PW',
            'passphrasePkcs8': 'PX',
            'keyOptions.majorKey': ('FS', ExcryptMap.MajorKeys.get),
            'keyOptions.keyUsage': ('CY', ExcryptMap.KeyUsageMulti.get),
            'data': 'CE',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'CO': 'certsImported',
            'PK': 'privateKeysImported',
            'IS': 'certsIgnored',
        }

        super().__init__(server_interface, 'Certificates', 'RKUP', request_map, response_map)


class RetrieveDNProfileTranslator(BaseTranslator):
    """
    JSON to Excrypt map for retrieving a DN profile with RKDV
    """

    request_schema = schemas.RetrieveDNProfile(unknown=EXCLUDE)

    def __init__(self, server_interface):
        # The translator for RAUP (CreatePKIRequest) uses this - update if you change things here
        request_map = {
            'name': 'NA',
            'id': 'ID',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'NA': 'name',
            'ID': 'id',
            'DN': ('subject', regauth_parsers.parse_subject),
        }

        super().__init__(server_interface, 'DNProfiles', 'RAVD', request_map, response_map)


class EncryptRSATranslator(BaseTranslator):

    request_schema = schemas.RSAEncryptDecrypt(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            # NA xor (CA and (RT xor AL))
            'pkiTree': 'CA',
            'certId': 'NA',
            'certCommonName': 'RT',
            'certAlias': 'AL',
            'hashType': 'RG',
            'data': 'BO',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'BO': 'result',
        }

        super().__init__(server_interface, 'Certificates', 'RKRE', request_map, response_map)


class EncryptECIESTranslator(BaseTranslator):

    request_schema = schemas.ECIESEncrypt(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            # NA xor (CA and (RT xor AL))
            'pkiTree': 'CA',
            'certId': 'NA',
            'certCommonName': 'RT',
            'certAlias': 'AL',
            'derivedKeyHashType': ('RG', ExcryptMap.ECIESHashTypes.get),
            'sharedInfo': 'AK',
            'iterationCount': 'IC',
            'data': 'BO',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'BO': 'result',
            'RD': 'ephemeralPublicKey',
        }

        super().__init__(server_interface, 'Certificates', 'RKVE', request_map, response_map)


class DecryptRSATranslator(BaseTranslator):

    request_schema = schemas.RSAEncryptDecrypt(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            # NA xor (CA and (RT xor AL))
            'pkiTree': 'CA',
            'certId': 'NA',
            'certCommonName': 'RT',
            'certAlias': 'AL',
            'hashType': 'RG',
            'data': 'BO',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'BO': 'result',
        }

        super().__init__(server_interface, 'Certificates', 'RKRD', request_map, response_map)


class DecryptECIESTranslator(BaseTranslator):

    request_schema = schemas.ECIESDecrypt(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            # NA xor (CA and (RT xor AL))
            'pkiTree': 'CA',
            'certId': 'NA',
            'certCommonName': 'RT',
            'certAlias': 'AL',
            'derivedKeyHashType': ('RG', ExcryptMap.ECIESHashTypes.get),
            'sharedInfo': 'AK',
            'iterationCount': 'IC',
            'data': 'BO',
            'ephemeralPublicKey': 'RD',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'BO': 'result',
        }

        super().__init__(server_interface, 'Certificates', 'RKVD', request_map, response_map)


class GenerateSignatureTranslator(BaseTranslator):

    request_schema = schemas.GenerateSignature(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'pkiTree': 'CA',
            'certId': 'NA',
            'certCommonName': 'RT',
            'certAlias': 'AL',
            'dataIsHashed': ('HS', parsers.serialize_reverse_bool),
            'hashType': ('RG', ExcryptMap.HashTypes.get),
            'padding': ('ZA', ExcryptMap.PaddingMode.get),
            'data': 'RF',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'RH': 'result',
        }

        super().__init__(server_interface, 'Certificates', 'RKGS', request_map, response_map)


class VerifyRSATranslator(BaseTranslator):

    request_schema = schemas.RSAVerify(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'pkiTree': 'CA',
            'certId': 'NA',
            'certCommonName': 'RT',
            'certAlias': 'AL',
            'hashType': ('RG', ExcryptMap.RSAVerifyHashTypes.get),
            'digestHash': ('CT', ExcryptMap.RSAVerifyHashTypes.get),
            'padding': ('ZA', ExcryptMap.RSAVerifyPadding.get),
            'saltLength': 'ZB',
            'data': 'RF',
            'signature': 'RH',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
        }

        super().__init__(server_interface, 'Certificates', 'RKRV', request_map, response_map)

    def preprocess_request(self, request):
        request['digestHash'] = 'None'

        # Update hash type and digest hash if the data is hashed.
        if request.get('dataIsHashed', False):
            request['digestHash'] = request['hashType']
            request['hashType'] = 'None'

        return request


class VerifyECCTranslator(BaseTranslator):

    request_schema = schemas.ECCVerify(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'pkiTree': 'CA',
            'certId': 'NA',
            'certCommonName': 'RT',
            'certAlias': 'AL',
            'hashType': ('RG', ExcryptMap.ECIESHashTypes.get),
            'digestHash': ('CT', ExcryptMap.ECIESHashTypes.get),
            'data': 'RF',
            'signature': 'RH',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
        }

        super().__init__(server_interface, 'Certificates', 'RKVV', request_map, response_map)

    def preprocess_request(self, request):
        request['digestHash'] = request['hashType']

        # Set hash type to none if data is hashed
        if request.get('dataIsHashed', False):
            request['hashType'] = 'None'

        return request


class CreateRandomKeyTranslator(BaseTranslator):
    """
    JSON to Excrypt map for creating a Symmetric Key
    """

    request_schema = schemas.CreateRandomKey(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'keyGroupId': 'KG',
            'keyName': 'KN',
            'keyType': ('TY', ExcryptMap.KeyTypes.get),
            'majorKey': ('FS', ExcryptMap.MajorKeys.get),
            'algorithm': ('CT', ExcryptMap.KeyAlgorithms.get),
            'keyUsage': 'CZ',
            'clearExport': 'SF',
            'validityPeriod.start': 'VS',
            'validityPeriod.end': 'VE',
            'owner': 'WN',
            'mailAddress': 'AD',
            'attributes': ('AT', regauth_parsers.serialize_key_attributes),
            'tr31Header': 'HE',
            'creationMode': 'CM',
            'modifier': ('AS', '{:>02X}'.format),
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'AE': 'checksum',
            'BG': 'keyblock',
        }

        super().__init__(server_interface, 'Keys', 'RKCK', request_map, response_map)

    def preprocess_request(self, request):
        # Ensure creation mode is set to "Generated"
        request['creationMode'] = 2

        # Map the key usage to the excrypt value
        ExcryptMap.KeyUsage.symmetric_preprocess(request)

        # Update key modifier based on key type
        key_type_value = int(ExcryptMap.KeyTypes.get(request['keyType'], 0))
        key_type = ExcryptMap.DeviceKeyType.from_int(key_type_value)
        request['modifier'] = ExcryptMap.DeviceKeyTypeModifier.get(key_type, 0)

        # Update security usage if clear exportable is true
        if request.get('clearExport', False):
            request['clearExport'] = '0x10'
        else:
            request['clearExport'] = '0x0'

        return request

    def finalize_response(self, response):
        # Legacy support, keyId is actually the name
        if response.get('status', 'N') == 'Y':
            response['id'] = self.raw_request.get('keyName', '')

        return response


class CreateRandomProtectedKeyTranslator(BaseTranslator):
    """
    JSON to Excrypt map for creating a Symmetric Protected Key
    """

    request_schema = schemas.CreateRandomProtectedKey(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            "operation": "OP",
            "keyGroupId": "GI",
            "keyGroup": "KG",
            "keyName": "NA",
            "owner": "WN",
            "mailAddress": "AD",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "AE": "checksum",
            "KI": "id",
            "BG": "keyblock",
        }

        super().__init__(server_interface, "Keys", "CLKY", request_map, response_map)

    def preprocess_request(self, request):
        # Ensure creation mode is set to "Generated"
        request["operation"] = "create"
        return request


class ExportSymmetricKeyTranslator(BaseTranslator):
    """
    JSON to Excrypt map for retrieving symmetric key info
    """

    request_schema = schemas.ExportSymmetricKey(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'keyId': 'KN',
            'keyGroupId': 'KG',
            'hostname': 'HO',
            'transferKey': 'HK',
            'format': ('FM', ExcryptMap.CryptogramExportType.get),
            'akbHeader': 'HE',
            'useCbc': ('BC', lambda b: 'Y' if b else 'N'),
            'checksumLength': 'AD',
            'returnKeyGroup': ('WG', lambda b: '1' if b else '0'),
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'KN': 'keyName',
            'KG': 'keyGroup',
            'BG': 'keyBlock',
            'AE': 'checksum',
            'KT': ('keyType', ExcryptMap.KeyTypes.get_reverse),
            'AS': ('modifier', '0x{:>02X}'.format),
            'AT': ('attributes', parsers.parse_key_value_csv),
            'CZ': 'keyUsage',
            'SF': 'securityUsage',
            'MK': ('majorKey', ExcryptMap.MajorKeys.get_reverse),
            'CT': ('algorithm', ExcryptMap.KeyAlgorithms.get_reverse),
            'TS': 'validityPeriod.start',
            'TE': 'validityPeriod.end',
            'CM': ('template', parsers.parse_bool),
        }
        super().__init__(server_interface, 'Keys', 'RKRC', request_map, response_map)

    def finalize_response(self, response):
        ExcryptMap.KeyUsage.symmetric_finalize(response)

        # Legacy support, keyId is actually the name
        if 'keyName' in response:
            response['keyId'] = response['keyName']

        # If there is more than one usage, choose one to return
        if 'securityUsage' in response:
            usage = int(response['securityUsage'], 16)
            for name, flag in ExcryptMap.SecurityUsage.items():
                if flag and flag & usage:
                    response['securityUsage'] = name
                    break
            else:
                response['securityUsage'] = 'None'

        return response


class ExportSymmetricProtectedKeyTranslator(BaseTranslator):
    """
    JSON to Excrypt map for retrieving symmetric protected key info
    """

    request_schema = schemas.ExportSymmetricProtectedKey(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            "keyId": "KI",
            "keyName": "NA",
            "transferKey": "WK",
            "format": ("FM", ExcryptMap.ProtectedKeyExportType.get),
            'randomPassphrase': ('MP', parsers.serialize_bool),
            'passphrase': 'PW',
            "operation": "OP",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "keyName",
            "KI": "keyId",
            "KG": "keyGroup",
            "GI": "keyGroupId",
            "BG": "keyBlock",
            "AE": "checksum",
            "CY": ("keyUsage", ExcryptMap.KeyUsageMulti.get_reverse),
            "KT": ("algorithm", ExcryptMap.KeyAlgorithmsV2.get_reverse),
            "VS": "validityPeriod.start",
            "VE": "validityPeriod.end",
        }
        super().__init__(server_interface, "Keys", "CLKY", request_map, response_map)

    def preprocess_request(self, request):
        request["operation"] = "export"
        return request


class ImportProtectedKeyTranslator(BaseTranslator):
    """
    JSON to Excrypt map for creating a Symmetric Protected Key by importing it
    """

    request_schema = schemas.ImportProtectedKey(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            "operation": "OP",
            "keyGroupId": "GI",
            "keyGroup": "KG",
            "keyName": "NA",
            "data": "BG",
            "format": ("FM", ExcryptMap.ProtectedKeyExportType.get),
            "wrappingKey": "WK",
            "wrappingKeyGroup": "WG",
            "passphrase": "PW",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "AE": "checksum",
            "KI": "id",
        }

        super().__init__(server_interface, "Keys", "CLKY", request_map, response_map)

    def preprocess_request(self, request):
        # Ensure creation mode is set to "Import"
        request["operation"] = "add"
        return request


class RetrieveSymmetricProtectedKeyGroupTranslator(BaseTranslator):
    """
    JSON to Excrypt map for retrieving symmetric protected key info
    """

    request_schema = schemas.RetrieveSymmetricProtectedKeyGroup(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            "keyGroupId": "GI",
            "keyGroup": "NA",
            "format": ("FM", ExcryptMap.ProtectedKeyRetrieveType.get),
            'randomPassphrase': ('MP', parsers.serialize_bool),
            'passphrase': 'PW',
            "operation": "OP",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "keyName",
            "KI": "keyId",
            "KG": "keyGroup",
            "GI": "keyGroupId",
            "BG": "keyBlock",
            "AE": "checksum",
            "CY": ("keyUsage", ExcryptMap.KeyUsageMulti.get_reverse),
            "KT": ("algorithm", ExcryptMap.KeyAlgorithmsV2.get_reverse),
            "VS": "validityPeriod.start",
            "VE": "validityPeriod.end",
        }
        super().__init__(server_interface, "Keys", "CLGR", request_map, response_map)

    def preprocess_request(self, request):
        request["operation"] = "retrieve"
        return request


class GeneralEncryptionTranslator(BaseTranslator):
    """
    JSON to Excrypt map for encryption with a symmetric key
    """

    request_schema = schemas.GeneralEncryptDecrypt(unknown=EXCLUDE)

    def __init__(self, server_interface):
        request_map = {
            'keyGroupId': 'KG',
            'keyId': 'KN',
            'padding': ('BT', parsers.serialize_bool),
            'cipher': ('BJ', ExcryptMap.Cipher.get),
            'data': 'BO',
            'dataFormat': ('DF', ExcryptMap.DataFormat.get),
            'mode': 'BF',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'KG': 'keyGroupId',
            'KN': 'keyId',
            'BT': ('padding', parsers.parse_bool),
            'BJ': ('cipher', ExcryptMap.Cipher.get_reverse),
            'AE': 'checksum',
            'BO': 'result',
        }

        super().__init__(server_interface, 'Keys', 'internal_RKED', request_map, response_map)

class ListCertificatesTranslator(BaseTranslator):
    """
    JSON to Excrypt map for listing PKICerts under a given CA
    """
    request_schema = schemas.ListCertificates(unknown=EXCLUDE)

    def __init__(self, server_interface):

        fixed_values = {
            'MN': 'X509CERT',
            'LG': '1',  # also return the container name
        }
        request_map = {
            'page': ('CH', (1).__rsub__),  # pages start at 1, chunks start at 0
            'pageCount': 'CS',
            'pkiTree': 'GN',
            'parent': 'PN',
        }
        response_map = {
            'AN': 'status',
            'BB': 'message',
            'NA': ('certificates.name', parsers.parse_csv),
            'CT': ('totalPages', int),
            'TO': ('totalItems', int),
        }

        super().__init__(
            server_interface, 'Certificates', 'RKLN', request_map, response_map, fixed_values
        )

    def finalize_response(self, response):
        if response.get('status', 'N') != 'Y':
            return response

        # when filtering by parent, the parent is included in the total (not present in the result list)
        if self.raw_request.get('parent', False):
            response['totalItems'] = max(0, response.getFieldAsInt('totalItems') - 1)

        response['certificates'] = parsers.unpivot_dict(response['certificates'])

        return response


