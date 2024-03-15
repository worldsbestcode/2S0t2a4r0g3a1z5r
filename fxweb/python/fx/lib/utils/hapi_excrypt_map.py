"""
@file      lib/utils/hapi_options_map.py
@author    Ryan Sargent (rsargent@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Provides a mapping of front-end values to excrypt values.
"""

import enum

from .data_structures import DisplayEnum, FxEnum, ImmutableBidict

AsymHashTypes = ImmutableBidict({
    'MD5': 'MD5',
    'RIPEMD-160': 'RIPEMD',
    'SHA-1': 'SHA1',
    'SHA-224': 'SHA224',
    'SHA-256': 'SHA256',
    'SHA-384': 'SHA384',
    'SHA-512': 'SHA512',
})

ECCCurveType = {
    'prime192v1': 'ECC 192',
    'secp224r1': 'ECC 224',
    'prime256v1': 'ECC 256',
    'secp384r1': 'ECC 384',
    'secp521r1': 'ECC 521',
    '1.2.840.10045.3.1.1': 'ECC 192',
    '1.3.132.0.33': 'ECC 224',
    '1.2.840.10045.3.1.7 ': 'ECC 256',
    '1.3.132.0.34': 'ECC 384',
    '1.3.132.0.35': 'ECC 521',
}

ECCCurveNames = ImmutableBidict({
    'ECC 192': 'prime192v1',
    'ECC 224': 'secp224r1',
    'ECC 256': 'prime256v1',
    'ECC 384': 'secp384r1',
    'ECC 521': 'secp521r1',
})

CertRequestTypes = ImmutableBidict({
    'PKI': 'PKI',
})

Cipher = ImmutableBidict({
    'ECB': '0',
    'CBC': '1',
    'CFB': '2',
    'CFB1': '3',
    'CFB8': '4',
    'CFB64': '5',
    'CFB128': '6',
    'OFB': '7',
})

CryptogramExportType = ImmutableBidict({
    'Cryptogram': '0',
    'AKB': '1',
    'TR-31': '2',
    'Clear': '3',
})

DataFormat = ImmutableBidict({
    'raw': '0',
    'DPM': '1',
})

ECIESHashTypes = ImmutableBidict({
    'None': 'None',
    'SHA-1': 'SHA-1',
    'SHA-244': 'SHA-244',
    'SHA-256': 'SHA-256',
    'SHA-384': 'SHA-384',
    'SHA-512': 'SHA-512',
})

HashTypes = ImmutableBidict({
    'SHA-1': '1',
    'MD5': '2',
    'RIPEMD-160': '3',
    'SHA-256': '4',
    'SHA-384': '5',
    'SHA-512': '6',
    'SHA-224': '7',
})

KeyAlgorithms = ImmutableBidict({
    'DES': '1',
    '2TDES': '2',
    '3TDES': '3',
    'AES-128': '4',
    'AES-192': '5',
    'AES-256': '6',
})

KeyAlgorithmsV2 = ImmutableBidict({
    'DES': 'DES',
    '2TDES': '2DES3',
    '3TDES': '3DES3',
    'AES-128': 'AES-128',
    'AES-192': 'AES-192',
    'AES-256': 'AES-256',
})

KeyTypes = ImmutableBidict({
    'Empty': '0',
    'Derivation key': '16',
    'Data encryption key': '10',
    'Message authentication key (MAC key)': '4',
    'Key encryption key': '6',
})

class KeyUsage:
    Asymmetric = ImmutableBidict({
        'Decrypt': 'D',
        'Derive': 'X',
        'Encrypt': 'E',
        'Encrypt/Decrypt': 'B',
        'None': '0',
        'Sign': 'G',
        'Sign/Verify': 'S',
        'Unwrap': '2',
        'Verify': 'V',
        'Wrap': '1',
        'Wrap/Unwrap': '3',
    })

    # Map of symmetric usage to excrypt usage and default modifier
    Symmetric = ImmutableBidict({
        'Decrypt': ('D', 0x02),
        'Derive': ('X', 0x08),
        'Encrypt': ('E', 0x02),
        'Encrypt/Decrypt': ('B', 0x02),
        'MAC Generate': ('G', 0x03),
        'MAC Generate/Verify': ('C', 0x03),
        'MAC Verify': ('V', 0x03),
        'Unwrap': ('D', 0x00),
        'Wrap': ('E', 0x00),
        'Wrap/Unwrap': ('B', 0x00),
        # This is almost always invalid
        'None': ('0', 0x00),
    })

    @classmethod
    def symmetric_preprocess(cls, request, usage='keyUsage', preserve_none=False):
        # Don't modify if there's no key usage value sent in
        if usage not in request:
            return

        # FXCryptogramValidator::validateKeyInfo considers explicitly giving None usage an error
        # removing it will then use the default for that modifier, which can actually be None
        if request[usage] in ('0', 'None') and not preserve_none:
            del request[usage]

        # Only assign the usage. The default modifier is from the key type
        if usage in request:
            request[usage], _ = cls.Symmetric.get(request[usage], ('0', 0))

    @classmethod
    def symmetric_finalize(cls, response, usage='keyUsage', modifier='modifier'):
        # Only modify if we have the values we need
        if usage not in response and modifier not in response:
            return

        response[usage] = cls.from_usage_and_modifier(response[usage], response[modifier])

    @classmethod
    def from_usage_and_modifier(cls, usage: str, modifier: str):
        # This should match the result of FirmwareUtils::getKeyUsageString for symmetric keys
        modifier = int(modifier, 16)
        if usage in ('D', 'E', 'B'):
            modifier = 0x02 if modifier else 0x00
        elif usage in ('G', 'C', 'V'):
            modifier = 0x03
        elif usage == 'X':
            modifier = 0x08
        else:
            modifier = 0

        return cls.Symmetric.get_reverse((usage, modifier), 'None')


KeyUsageMulti = ImmutableBidict({
    'None': '0',
    'Derive': 'X',
    'Encrypt/Decrypt': 'ED',
    'Encrypt': 'E',
    'Decrypt': 'D',
    'Sign/Verify': 'SV',
    'Sign': 'S',
    'Verify': 'V',
    'Wrap/Unwrap': 'WU',
    'Wrap': 'W',
    'Unwrap': 'U',
})

MajorKeys = ImmutableBidict({
    'MFK': '1',
    'PMK': '6',
    'FTK': '7',
})

PaddingMode = ImmutableBidict({
    'None': '0',
    'PKCS #1': '1',
    # 'Bit': '2',
    # 'Zero': '3',
    # 'OAEP': '4',
    # 'ZeroIfReq': '5',
    'PSS': '6',
    'X9.31': '7',
})

DaysOfWeek = {
    'Sunday': 0x1,
    'Monday': 0x2,
    'Tuesday': 0x4,
    'Wednesday': 0x8,
    'Thursday': 0x10,
    'Friday': 0x20,
    'Saturday': 0x40,
}

TimeUnits = ImmutableBidict({
    "Millisecond":"Millisecond",
    "Milliseconds":"Milliseconds",
    "Second": "Second",
    "Seconds": "Seconds",
    "Minute": "Minute",
    "Minutes": "Minutes",
    "Hour": "Hour",
    "Hours": "Hours",
    "Day": "Day",
    "Days": "Days",
    "Week": "Week",
    "Weeks": "Weeks",
    "Month": "Month",
    "Months": "Months",
    "Year": "Year",
    "Years": "Years",
})


class PkiCertType(FxEnum):
    """
    Remotekey enum PKICert::TYPE
    """
    _columns =                                'int', 'typeToStr'

    X509CertLocal            = 'X.509',           0, 'X.509'
    EMVCertVisa              = 'EMV Visa',        1, 'Visa EMV'
    EMVCertAmex              = 'EMV Amex',        2, 'Amex EMV'
    EMVCertMC                = 'EMV MC',          3, 'MasterCard EMV'
    EMVCertJCB               = 'EMV JCB',         4, 'JCB EMV'
    EMVCertMultiBanco        = 'EMV Multibanco',  5, 'MultiBanco EMV'
    SCSARoot                 = 'SCSA KIC Root',   6, 'SCSA Root'
    SCSAUpperLevel           = 'SCSA UL',         7, 'SCSA Upper Level'
    EMVCertUPI               = 'EMV UPI',         8, 'UPI EMV'
    X509CertExternalDigiCert = 'DigiCert',        9, 'External DigiCert X.509'
    X509CertExternalWCCE     = 'WCCE',           10, 'External WCCE X.509'


RSAHashTypes = ImmutableBidict({
    'SHA-1': 'SHA-1',
    'SHA-256': 'SHA-256',
    'SHA-512': 'SHA-512',
})

RSAVerifyHashTypes = ImmutableBidict({
    'None': 'None',
    'SHA-1': 'SHA-1',
    'SHA-224': 'SHA-224',
    'SHA-256': 'SHA-256',
    'SHA-384': 'SHA-384',
    'SHA-512': 'SHA-512',
})

SignaturePadding = ImmutableBidict({
    'PKCS #1': 'PKCS1',
    'PSS': 'PSS',
    'X9.31': 'X931',
})

ProtectedKeyExportType = ImmutableBidict({
    'Cryptogram': 'fxgcm',
    'Clear': 'clear',
    'PKCS12': 'pkcs12',
})

ProtectedKeyRetrieveType = ImmutableBidict({
    'Clear': 'clear',
    'PKCS12': 'pkcs12',
})

RSAVerifyPadding = ImmutableBidict({
    'None': 'None',
    'PKCS #1': 'PKCS1',
    'PSS': 'PSS',
    'X9.31': 'X931',
})

SecurityUsage = ImmutableBidict({
    'None': 0x00,
    'Private': 0x01,
    'Sensitive': 0x02,
    'Immutable': 0x04,
    'Password Export': 0x08,
    'Clear Key Export': 0x10,
    'Anonymous Signing': 0x20,
})

ApprovableObjectTypes = ImmutableBidict({
    # ManagedObject::TYPE to str repr in ApprovalManagerView for type column
    "90": "X.509",
    "93": "Hash",
})

V3ExtensionModes = ImmutableBidict({
    "Optional": "OPTIONAL",
    "Fixed": "FIXED",
    "Required": "REQUIRED",
    "Restricted": "RESTRICTED",
})


CrlTimeUnits = ImmutableBidict({
    "Minute": "Minute",
    "Minutes": "Minutes",
    "Day": "Day",
    "Days": "Days",
    "Hour": "Hour",
    "Hours": "Hours",
    "Month": "Month",
    "Months": "Months",
    "Year": "Year",
    "Years": "Years"
})


class RevocationReasons(FxEnum):
    _columns =                                          "int",  "items"
    unspecified =               "unspecified",          0,      "Unspecified"
    key_compromise =            "keyCompromise",        1,      "Key Compromise"
    ca_compromise =             "cACompromise",         2,      "CA Compromise"
    affiliation_changed =       "affiliationChanged",   3,      "Affiliation Changed"
    superseded =                "superseded",           4,      "Superseded"
    cessation_of_Operation =    "cessationOfOperation", 5,      "Cessation of Operation"
    certificate_hold =          "certificateHold",      6,      "Certificate Hold"
    unused =                    "unused",               7,      "Unused"
    remove_from_crl =           "removeFromCRL",        8,      "RemoveFromCRL"
    privilege_withdrawn =       "privilegeWithdrawn",   9,      "Privilege Withdrawn"
    aa_compromise =             "aACompromise",         10,     "AA Compromise"


class RKGCHashTypes(DisplayEnum):
    """
    Remotekey enum APIHashTypes::RKGC
    """
    SHA_1   = 1, 'SHA-1'
    SHA_256 = 3, 'SHA-256'
    SHA_224 = 4, 'SHA-224'
    SHA_384 = 5, 'SHA-384'
    SHA_512 = 6, 'SHA-512'


class ECCCurveId(DisplayEnum):
    """
    Remotekey enum ECC_CURVE_ID (ECCDefs.h)

    Strings from openssl (mapped via CryptoUtils::getNIDFromCurve)
    """
    T_PRIME_192 = 0, 'prime192v1', 'NIST/X9.62/SECG curve over a 192 bit prime field'
    T_PRIME_224 = 1, 'secp224r1',  'NIST/SECG curve over a 224 bit prime field'
    T_PRIME_256 = 2, 'prime256v1', 'X9.62/SECG curve over a 256 bit prime field'
    T_PRIME_384 = 3, 'secp384r1',  'NIST/SECG curve over a 384 bit prime field'
    T_PRIME_521 = 4, 'secp521r1',  'NIST/SECG curve over a 521 bit prime field'


class X509KeyUsage(DisplayEnum):
    """
    Remotekey defines from CommonDefs.h

    Strings from X509CertFields::mapKeyUsagesToNames
    """
    KU_ENCIPHER_ONLY     = 0x0001, 'Encipher Only'
    KU_CRL_SIGN          = 0x0002, 'CRL Sign'
    KU_KEY_CERT_SIGN     = 0x0004, 'Certificate Sign'
    KU_KEY_AGREEMENT     = 0x0008, 'Key Agreement'
    KU_DATA_ENCIPHERMENT = 0x0010, 'Data Encipherment'
    KU_KEY_ENCIPHERMENT  = 0x0020, 'Key Encipherment'
    KU_NON_REPUDIATION   = 0x0040, 'Non Repudiation'
    KU_DIGITAL_SIGNATURE = 0x0080, 'Digital Signature'
    KU_DECIPHER_ONLY     = 0x8000, 'Decipher Only'

    @classmethod
    def serialize_usage(cls, usage: dict) -> str:
        result = ', '.join(filter(usage.get, usage.keys() - {'Critical'}))
        if result and usage.get('Critical'):
            # critical needs to be the first token
            result = 'critical, ' + result
        return result


# Name to ASN.1 OID map of common relative distinguished names:
DefaultRDNs = {
    # Defined in RFC 4514:
    'C': '2.5.4.6',
    'countryName': '2.5.4.6',
    'CN': '2.5.4.3',
    'commonName': '2.5.4.3',
    'DC': '0.9.2342.19200300.100.1.25',
    'domainComponent': '0.9.2342.19200300.100.1.25',
    'L': '2.5.4.7',
    'localityName': '2.5.4.7',
    'O': '2.5.4.10',
    'organizationName': '2.5.4.10',
    'OU': '2.5.4.11',
    'organizationalUnitName': '2.5.4.11',
    'ST': '2.5.4.8',
    'stateOrProvinceName': '2.5.4.8',
    'STREET': '2.5.4.9',
    'streetAddress': '2.5.4.9',
    'UID': '0.9.2342.19200300.100.1.1',
    'userId': '0.9.2342.19200300.100.1.1',

    'GN': '2.5.4.42',
    'givenName': '2.5.4.42',
    'MAIL': '1.2.840.113549.1.9.1',
    'emailAddress': '1.2.840.113549.1.9.1',
    'SN': '2.5.4.4',
    'surname': '2.5.4.4',
    'T': '2.5.4.12',
    'title': '2.5.4.12',
}


FixedDNOIDTypes = {
    # Restrict the ASN.1 Types of given OIDs (defined in RFC 5280)
    # Options are taken via Remotekey's X509DNDict
    # OIDs not listed here should default to 12 (UTF-8)

    # Default to PrintableString:
    '2.5.4.6': '19',  # Country
    '2.5.4.46': '19',  # DN Qualifier
    '2.5.4.5': '19',  # Serial
    '2.5.4.20': '19',  # Telephone Number
    '2.5.4.45': '19',  # X.500 Unique Identifier

    # Default to IA5 String:
    '0.9.2342.19200300.100.1.25': '22',  # Domain Component
    '1.2.840.113549.1.9.1': '22',  # Email
}

class ASN1Types(DisplayEnum):
    """
    Remotekey enum ASN1Type::Type
    """
    UTF8String      = 12, 'UTF8String'
    NumericString   = 18, 'NumericString'
    PrintableString = 19, 'PrintableString'
    T61String       = 20, 'T61String'
    IA5String       = 22, 'IA5String'
    # VisibleString (26) not accepted by firmware
    UniversalString = 28, 'UniversalString'


class KeyGroupRetrievalMethod(DisplayEnum):
    """
    Remotekey enum KeyGroup::RetrievalMethod

    Strings from KeyGroup::getKRAString
    """
    RM_NONE     = 0, 'None'
    RM_HOST     = 1, 'Host'
    RM_STE      = 2, 'Soonest to expire'
    RM_ORDERED  = 3, 'Ordered'
    RM_REGEN    = 4, 'Regenerative'
    RM_UNIQUE   = 5, 'Unique'

    def is_key_store(self):
        return self in (KeyGroupRetrievalMethod.RM_REGEN, KeyGroupRetrievalMethod.RM_UNIQUE)


class DeviceKeyType(FxEnum):
    """
    Remotekey enum DeviceKeyType::TYPE

    Strings from key types in rk-common/keys/utils/KeyJsonFilterApi.h
    in rk-common/objects/DeviceKeyType.cpp
    """
    _columns =                                              ('int', )
    UNKNOWN                 = 'Unknown',                    0
    MASTER_SESSION_KEY      = 'MasterSession',              1
    DUKPT_INITIAL_KEY       = 'DukptInitial',               2
    DUKPT_BDK_KEY           = 'DukptBdk',                   3
    MAC_KEY                 = 'MacKey',                     4
    PIN_ENCRYPTION_KEY      = 'PinEncryption',              5
    KEY_TRANSFER_KEY        = 'KeyTransfer',                6
    HOST_VERIFICATION_KEY   = 'HostVerification',           7
    DUKPT_3DES_BDK_KEY      = 'Dukpt3desBdk',               8
    DEFAULT_KTK             = 'DefaultKtk',                 9
    DATA_ENCRYPTION_KEY     = 'DataEncryption',             10
    DATA_DECRYPTION_KEY     = 'DataDecryption',             11
    DETACH_BDK_KEY          = 'DetachBdkKey',               12
    TERMINAL_MASTER_KEY     = 'TerminalMaster',             13
    SERIAL_NUMBER_BDK       = 'SerialNumberBdk',            14
    IV_BDK_KEY              = 'IvBdk',                      15
    GENERIC_BDK             = 'GenericBdk',                 16
    PIN_GENERATION_KEY      = 'PinGeneration',              17
    XAC_DKLK                = 'XacDklk',                    18
    TRADE_ROOT_DUKPT        = 'TradeRoot',                  19
    AEVI_KBPK               = 'AeviKbpk',                   20
    INITIALIZATION_VECTOR   = 'InitializationVector',       21
    DECIMALIZATION_TABLE    = 'DecimalizationTable',        22
    FILE_ENCRYPTION_MODE0   = 'FileEncryption',             23
    CLOUD_KEY_TRANSFER_KEY  = 'HsmProtectedKeyTransfer',    24
    AES_DUKPT_BDK           = 'AesDukptBdk',                25
    AES_DUKPT_INITIAL       = 'AesDukptInitial',            26
    GENERIC_APP_KEY         = 'GenericAppKey',              27
    FILE_ENCRYPTION_MODE1   = 'FileEncryptionV2',           28
    RSA                     = 'Rsa',                        29


# Converts the device key type to the default modifier
# This is taken from the values in DeviceKeyTypeUtils::initialize
DeviceKeyTypeModifier = {
    DeviceKeyType.UNKNOWN:  0x00,
    DeviceKeyType.MASTER_SESSION_KEY:  0x00,
    DeviceKeyType.DUKPT_INITIAL_KEY:  0x08,
    DeviceKeyType.DUKPT_BDK_KEY:  0x08,
    DeviceKeyType.MAC_KEY:  0x03,
    DeviceKeyType.PIN_ENCRYPTION_KEY:  0x01,
    DeviceKeyType.KEY_TRANSFER_KEY:  0x00,
    DeviceKeyType.HOST_VERIFICATION_KEY:  0x00,
    DeviceKeyType.DUKPT_3DES_BDK_KEY:  0x08,
    DeviceKeyType.DEFAULT_KTK:  0x00,
    DeviceKeyType.DATA_ENCRYPTION_KEY: 0x02,
    DeviceKeyType.DATA_DECRYPTION_KEY: 0x02,
    DeviceKeyType.DETACH_BDK_KEY: 0x0E,
    DeviceKeyType.TERMINAL_MASTER_KEY: 0x00,
    DeviceKeyType.SERIAL_NUMBER_BDK: 0x08,
    DeviceKeyType.IV_BDK_KEY: 0x08,
    DeviceKeyType.GENERIC_BDK: 0x08,
    DeviceKeyType.PIN_GENERATION_KEY: 0x09,
    DeviceKeyType.XAC_DKLK: 0x08,
    DeviceKeyType.TRADE_ROOT_DUKPT: 0x08,
    DeviceKeyType.AEVI_KBPK: 0x08,
    DeviceKeyType.INITIALIZATION_VECTOR: 0x06,
    DeviceKeyType.DECIMALIZATION_TABLE: 0x0F,
    DeviceKeyType.FILE_ENCRYPTION_MODE0: 0x00,
    DeviceKeyType.CLOUD_KEY_TRANSFER_KEY: 0x02,
    DeviceKeyType.AES_DUKPT_BDK: 0x08,
    DeviceKeyType.AES_DUKPT_INITIAL: 0x08,
    DeviceKeyType.GENERIC_APP_KEY: 0x00,
    DeviceKeyType.FILE_ENCRYPTION_MODE1: 0x02,
    DeviceKeyType.RSA: 0x00,
}


class GPKIKeyType(DisplayEnum):
    """
    Remotekey enum GPKIKeyType

    Strings from FirmwareUtils::expandGPKIKeyType
    """
    eGPKIKeyTypeUnknown  = -1, 'Unknown'
    eGPKIKeyTypeEmpty    =  0, 'Empty'
    eGPKIKeyTypeDES      =  1, 'Single DES'
    eGPKIKeyType2DES3    =  2, 'Double 3DES'
    eGPKIKeyType3DES3    =  3, 'Triple 3DES'
    eGPKIKeyTypeAES128   =  4, 'AES-128'
    eGPKIKeyTypeAES192   =  5, 'AES-192'
    eGPKIKeyTypeAES256   =  6, 'AES-256'
    eGPKIKeyTypeDiebold  =  7, 'Diebold Table'
    eGPKIKeyTypeRSA512   =  8, 'RSA-512'
    eGPKIKeyTypeRSA1024  =  9, 'RSA-1024'
    eGPKIKeyTypeRSA2048  = 10, 'RSA-2048'
    eGPKIKeyTypeRSA3072  = 11, 'RSA-3072'
    eGPKIKeyTypeRSA4096  = 12, 'RSA-4096'
    eGPKIKeyTypeEC       = 13, 'ECC'


class FWMajorKeySlot(DisplayEnum):
    """
    Remotekey enum FWMajorKeySlot

    Strings from FirmwareUtils::expandFWMajorKeySlot
    """
    eFWSlotClear = 0, 'Clear'
    eFWSlotMFK   = 1, 'MFK'
    eFWSlotKEK   = 2, 'KEK'
    eFWSlotBEK   = 3, 'BEK'
    eFWSlotPMFK  = 4, 'PMFK'
    eFWSlotSCEK  = 5, 'SCEK'
    eFWSlotPMK   = 6, 'PMK'
    eFWSlotFTK   = 7, 'FTK'


class FWSecUsage(enum.IntFlag):
    """
    Remotekey enum FWSecUsage
    """
    eFWSecUsageInvalid   = -1
    eFWSecUsageNone      = 0x00
    eFWSecUsagePrivate   = 0x01
    eFWSecUsageSensitive = 0x02
    eFWSecUsageImmutable = 0x04
    eFWSecUsagePWExport  = 0x08
    eFWSecUsageClear     = 0x10
    eFWSecUsageAnonSign  = 0x20
    eFWSecUsageAll       = 0x3F

class FWKeyUsage:
    """
    Remotekey enum FWUsage
    """
    # TODO(@dneathery): make this class more featureful and replace old keyusage dicts
    map_multi_asym = [
        # Do not change the order these appear in
        ('E', 'Encrypt'),
        ('D', 'Decrypt'),
        ('W', 'Wrap'),
        ('U', 'Unwrap'),
        ('S', 'Sign'),
        ('V', 'Verify'),
        ('X', 'Derive'),
    ]

    @classmethod
    def asym_multi_usage_to_name(cls, given: str):
        """
        Convert an AsymKeyUsageUnion multi-usage to canonical name. Ex: "VS" -> "Sign/Verify"
        """

        combined = '/'.join(name for usage, name in cls.map_multi_asym if usage in given)
        return combined or 'None'


class ObjectPermType(DisplayEnum):
    """
    Remotekey enum Permission::eObjectPermType

    Strings from PermissionUtils::getObjectTypeByName
    """
    ePermNone   = 0, 'None'
    ePermView   = 1, 'View'
    ePermUse    = 2, 'Use'
    ePermModify = 3, 'Modify'
    ePermDelete = 4, 'Delete'
    ePermAdd    = 5, 'Add'


class PermissionScope(DisplayEnum):
    """
    Remotekey enum Permission::ePermScope
    """
    ePermScopeNone      = 0, 'None'
    ePermScopeImmediate = 1, 'Immediate'
    ePermScopeRecursive = 2, 'Recursive'


class FpeAlgorithm(FxEnum):
    """
    Remotekey enum FpeAlgo
    """
    _columns =          'int',  'typeToStr'

    FF1         = 'FF1',    1,  'FF1'
    FF3_1       = 'FF3-1',  2,  'FF3_1'
    FXCMAC      = 'FXCMAC', 3,  'FxCMAC'
    RED         = 'RED',    4,  'RED'


class FilterClauseOperator(DisplayEnum):
    """
    Remotekey enum FilterClause::Operator
    """
    AND = 0, 'And'
    OR  = 1, 'Or'


class FilterClauseMatch(DisplayEnum):
    """
    Remotekey enum FilterClause::Match
    """
    PARTIAL         = 0, 'Contains'  # (field LIKE (%%value%%))
    EXACT           = 1, 'Equals'  # (field=value)
    NUMERIC_RANGE   = 2, 'Range'  # (field >= min AND field <= max)
    SET             = 3, 'Set'  # (field IN (va,lu,e))
    LESS_THAN       = 6, 'LessThan'  # (field < value)
    GREATER_THAN    = 7, 'GreaterThan'  # (field > value)
    LESS_EQUAL      = 8, 'LessEqual'  # (field <= value)
    GREATER_EQUAL   = 9, 'GreaterEqual'  # (field >= value)


MobileCarriers: set = {
    # CarrierFunctions::mCarrierToString
    "Alltell",
    "ATT",
    "Boost",
    "Comcast",
    "Qwest",
    "Sprint",
    "Tmobile",
    "Trac",
    "Verizon",
    "Virgin",
    "Rogers",
    "Vodacom",
    "MTNGroup",
    "Custom",
    "None",
}


class UserGroupStorageLocation(DisplayEnum):
    """
    user_group::StorageLocation

    Strings from UserGroup::astrLocationNames
    """
    StoredInDB   = 0, 'Database'
    StoredOnCard = 1, 'Card'
    StoredOnLDAP = 2, 'LDAP Server'


# TODO(@dneathery): Update when RKPS implemented
class ClassPermType(DisplayEnum):
    """
    Remotekey enum Permission::eClassPermType

    Strings from Permission::getClassPermTypeName
    Descriptions from PermissionManager::loadAll
    """
    ePermTypeLog            =  1, 'Log',                   'View logs'
    ePermTypeUser           =  2, 'User',                  'Manage users'
    ePermTypeConfig         =  3, 'Config',                'Update system configuration'
    ePermTypeBackup         =  4, 'Backup',                'Database backup'
    ePermTypeRestore        =  5, 'Restore',               'Database restore'
    ePermTypeHost           =  6, 'Host',                  'Manage hosts/networks'
    ePermTypeDevice         =  7, 'Device',                'Manage devices'
    ePermTypeCertManage     =  8, 'CertManage',            'Manage certificates'
    ePermTypeTemplate       =  9, 'Template',              'Manage templates'
    ePermTypeKey            = 11, 'Key',                   'Manage keys'
    ePermTypeCardGroup      = 12, 'CardGroup',             'Manage encryption device groups'
    ePermTypeDeviceHost     = 13, 'DeviceHost',            'Manage device hosts'
    ePermTypePeer           = 14, 'Peer',                  'View peers'
    ePermTypeReport         = 15, 'Report',                'Manage and print reports'
    ePermTypeLDAP           = 16, 'LDAP',                  'Manage LDAP entries and ACL'
    ePermTypeDatabase       = 17, 'Database',              'Manage databases'
    ePermTypeLDAPSchema     = 18, 'LDAPSchema',            'Manage LDAP schema'
    ePermTypeOrgUnit        = 19, 'OrgUnit',               'Manage organizational units and persons'
    ePermTypeTokenInventory = 20, 'TokenInventory',        'Manage smart tokens inventory'
    ePermTypeTokenProfile   = 21, 'TokenProfile',          'Manage smart tokens profiles'
    ePermTypeApprovalGroup  = 24, 'RequestApproval',       'Manage signing approvals'
    ePermTypeV3ExtProfile   = 25, 'V3ExtProfile',          'Manage X.509 v3 extension profiles'
    ePermTypeX509DNProfile  = 26, 'X509DNProfile',         'Manage X.509 DN profiles'
    ePermTypeLDAPDirectory  = 27, 'LDAPDirectory',         'Manage remote LDAP servers'
    ePermTypeNotifications  = 28, 'Notifications',         'Manage notifications'
    ePermTypeSecretData     = 29, 'SecretData',            'Manage secret data'
    ePermTypeKMIPTemplate   = 30, 'KMIPTemplate',          'Manage KMIP templates'
    ePermTypeToken          = 31, 'Token',                 'Tokenization'
    ePermTypeWindowsEnroll  = 33, 'WindowsPermission',     'Perform Windows enrollments'
    ePermTypeSFTPServer     = 34, 'SFTPServer',            'Use the system SFTP server'
    ePermTypeCrypto         = 35, 'Crypto',                'Perform cryptographic operations'
    ePermTypeFileEnc        = 36, 'FileEnc',               'File encryption'
    ePermTypePower          = 37, 'PowerControl',          'Shut down and reboot server'
    ePermTypeTLSProfile     = 38, 'TLSProfile',            'Manage TLS Profiles'
    ePermTypeTLSTunnel      = 39, 'CryptoTunnel',          'Manage CryptoTunnels'


# TODO(@dneathery): Update when RKPS implemented
class ClassPermFlag(DisplayEnum):
    """
    Remotekey enum Permission::eClassPermFlag

    Strings from Permission.cpp getDefaultFlagMap
    """
    ePermFlagNone            = 0x00000000, 'None'
    ePermFlagAdd             = 0x00000001, 'Add'
    ePermFlagDelete          = 0x00000002, 'Delete'
    ePermFlagModify          = 0x00000004, 'Modify'
    ePermFlagPrint           = 0x00000008, 'Print'
    ePermFlagExport          = 0x00000010, 'Export'
    ePermFlagDetokenize      = 0x00000010, 'Detokenize'
    ePermFlagInject          = 0x00000020, 'Inject'
    ePermFlagExportComponent = 0x00000040, 'ExportComponent'
    ePermFlagMassImport      = 0x00000080, 'MassImport'
    ePermFlagMassExport      = 0x00000100, 'MassExport'
    ePermFlagEthernet        = 0x00000200, 'Edit Ethernet Settings'
    ePermFlagNetwork         = 0x00000400, 'Edit Network Settings'
    ePermFlagTCP             = 0x00000800, 'Edit TCP Settings'
    ePermFlagSSL             = 0x00001000, 'Edit TLS Settings'
    ePermFlagExcryptAuth     = 0x00002000, 'Use Excrypt Authentication Port'
    ePermFlagRekey           = 0x00004000, 'RekeyCryptogram'
    ePermFlagImportComponent = 0x00008000, 'Import Components'
    ePermFlagUpload          = 0x00010000, 'Upload Certificate Signing Requests'
    ePermFlagApprove         = 0x00020000, 'Approve Certificate Signing Requests'
    ePermFlagKeyHeaderEdit   = 0x00040000, 'Edit Key Block Headers'
    ePermFlagExportClear     = 0x00080000, 'ExportClear'
    ePermFlagTokenize        = 0x00100000, 'Tokenize'
    ePermFlagVerify          = 0x00200000, 'Verify'
    ePermFlagEncrypt         = 0x00400000, 'Encrypt'
    ePermFlagDecrypt         = 0x00800000, 'Decrypt'
    ePermFlagSign            = 0x01000000, 'Sign'
    ePermFlagWrap            = 0x02000000, 'Wrap'
    ePermFlagUnwrap          = 0x04000000, 'Unwrap'


# TODO(@dneathery): Update when RKPS implemented
ClassPermMap = {
    # From PermissionUtils::getDefaultClassFlag
    ClassPermType.ePermTypeOrgUnit: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagExport,
        ClassPermFlag.ePermFlagInject,
        ClassPermFlag.ePermFlagExcryptAuth,
    },
    ClassPermType.ePermTypeCertManage: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagExport,
        ClassPermFlag.ePermFlagInject,
        ClassPermFlag.ePermFlagMassImport,
        ClassPermFlag.ePermFlagMassExport,
        ClassPermFlag.ePermFlagUpload,
        ClassPermFlag.ePermFlagExportClear,
    },
    ClassPermType.ePermTypeKey: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagExport,
        ClassPermFlag.ePermFlagExportComponent,
        ClassPermFlag.ePermFlagPrint,
        ClassPermFlag.ePermFlagMassImport,
        ClassPermFlag.ePermFlagMassExport,
        ClassPermFlag.ePermFlagRekey,
        ClassPermFlag.ePermFlagKeyHeaderEdit,
        ClassPermFlag.ePermFlagExportClear,
        ClassPermFlag.ePermFlagImportComponent,
    },
    ClassPermType.ePermTypeLog: {
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagExport,
    },
    ClassPermType.ePermTypeDevice: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagInject,
        ClassPermFlag.ePermFlagMassImport,
    },
    ClassPermType.ePermTypeHost: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagMassImport,
    },
    ClassPermType.ePermTypeUser: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagExportClear,
    },
    ClassPermType.ePermTypeSecretData: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagExportClear,
    },
    ClassPermType.ePermTypeCardGroup: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeDeviceHost: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeTemplate: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeDatabase: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeLDAP: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeLDAPSchema: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeLDAPDirectory: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeV3ExtProfile: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeX509DNProfile: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeNotifications: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeKMIPTemplate: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeTLSTunnel: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeTLSProfile: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeReport: {
        ClassPermFlag.ePermFlagModify,
    },
    ClassPermType.ePermTypeConfig: {
        ClassPermFlag.ePermFlagEthernet,
        ClassPermFlag.ePermFlagNetwork,
        ClassPermFlag.ePermFlagTCP,
        ClassPermFlag.ePermFlagSSL,
    },
    ClassPermType.ePermTypeTokenProfile: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagInject,
    },
    ClassPermType.ePermTypeTokenInventory: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagInject,
    },
    ClassPermType.ePermTypeApprovalGroup: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagApprove,
    },
    ClassPermType.ePermTypeToken: {
        ClassPermFlag.ePermFlagAdd,
        ClassPermFlag.ePermFlagDelete,
        ClassPermFlag.ePermFlagModify,
        ClassPermFlag.ePermFlagTokenize,
        ClassPermFlag.ePermFlagDetokenize,
        ClassPermFlag.ePermFlagVerify,
    },
    ClassPermType.ePermTypeCrypto: {
        ClassPermFlag.ePermFlagEncrypt,
        ClassPermFlag.ePermFlagDecrypt,
        ClassPermFlag.ePermFlagSign,
        ClassPermFlag.ePermFlagVerify,
        ClassPermFlag.ePermFlagWrap,
        ClassPermFlag.ePermFlagUnwrap,
    },
    ClassPermType.ePermTypeFileEnc: {
        ClassPermFlag.ePermFlagEncrypt,
        ClassPermFlag.ePermFlagDecrypt,
    },
    ClassPermType.ePermTypeBackup: {
        ClassPermFlag.ePermFlagNone,
    },
    ClassPermType.ePermTypeRestore: {
        ClassPermFlag.ePermFlagNone,
    },
    ClassPermType.ePermTypePeer: {
        ClassPermFlag.ePermFlagNone,
    },
    ClassPermType.ePermTypeWindowsEnroll: {
        ClassPermFlag.ePermFlagNone,
    },
    ClassPermType.ePermTypeSFTPServer: {
        ClassPermFlag.ePermFlagNone,
    },
    ClassPermType.ePermTypePower: {
        ClassPermFlag.ePermFlagNone,
    },
}


DUKPTTypes = ImmutableBidict({
    'None': '0',
    'PIN': '1',
    'Data': '2',
    'Response': '4',
})
