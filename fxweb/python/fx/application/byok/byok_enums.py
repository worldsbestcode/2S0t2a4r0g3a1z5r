"""
@file      byok/byok_enums.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Enums and Excrypt representations for VC BYOK
"""


class GPKIKeyType:
    _table = [
        # name,   value, private, public
        ('Empty',        0, '0', None),
        ('DES',          1, '1', None),
        ('2TDES',        2, '2', None),
        ('3TDES',        3, '3', None),
        ('AES-128',      4, 'A', None),
        ('AES-192',      5, 'B', None),
        ('AES-256',      6, 'C', None),
        ('Diebold',      7, 'D', None),
        ('RSA-512',      8, 'R',  'r'),
        ('RSA-1024',     9, 'S',  's'),
        ('RSA-2048',    10, 'T',  't'),
        ('RSA-3072',    11, 'U',  'u'),
        ('RSA-4096',    12, 'V',  'v'),
        ('ECC',         13, 'E',  'e'),
        ('Certificate', 14, 'X', None)
    ]
    names_to_values = {row[0]: row[1] for row in _table}
    values_to_names = {row[1]: row[0] for row in _table}
    sym_types = [row[0] for row in _table[1:7]]
    private_to_name = {row[2]: row[0] for row in _table}


MAJOR_KEY_CONSTS = {
    '1': 'MFK',
    '2': 'KEK',
    '3': 'BAK',
    '4': 'PMFK',
    '5': 'SCEK',
    '6': 'PMK',
    '7': 'FTK',
    '8': 'VMK',
}
MAJOR_KEY_CONSTS_REVERSED = {v: k for k, v in MAJOR_KEY_CONSTS.items()}


KEY_USAGE_FLAGS = {
    'E': 'Encrypt',
    'D': 'Decrypt',
    'W': 'Wrap',
    'U': 'Unwrap',
    'S': 'Sign',
    'V': 'Verify',
    'X': 'Derive',
}


KEY_USAGE_SYM_FLAGS = {
    # pre-sorted() lists for comparison
    'N': ['Decrypt', 'Derive', 'Encrypt', 'Sign', 'Unwrap', 'Verify', 'Wrap'],
    'B': ['Decrypt', 'Encrypt'],
    'D': ['Decrypt'],
    'E': ['Encrypt'],
    'C': ['Sign', 'Verify'],
    'G': ['Sign'],
    'V': ['Verify'],
    'X': ['Derive'],
    None: [],
    # uppercased in fw_sym_key_usage_from_name to alias encrypt/decrypt: 
    'b': ['Unwrap', 'Wrap'],
    'd': ['Unwrap'],
    'e': ['Wrap'],
}

KEY_USAGE_ASYM_FLAGS = {
    # pre-sorted() lists for comparison
    'N': ['Decrypt', 'Derive', 'Encrypt', 'Sign', 'Unwrap', 'Verify', 'Wrap'],
    'B': ['Decrypt', 'Encrypt'],
    'D': ['Decrypt'],
    'E': ['Encrypt'],
    'S': ['Sign', 'Verify'],
    'G': ['Sign'],
    'V': ['Verify'],
    'X': ['Derive'],
    '3': ['Unwrap', 'Wrap',],
    '2': ['Unwrap'],
    '1': ['Wrap'],
}

SEC_USAGE_FLAGS = (
    (0x01, 'Private'),
    (0x02, 'Sensitive'),
    (0x04, 'Immutable'),
    (0x08, 'Password Export'),  # Deprecated
    (0x10, 'Clear Key Export'),  # Deprecated
    (0x20, 'Anonymous Signing'),
)
SEC_USAGE_NAMES = [pair[1] for pair in SEC_USAGE_FLAGS if pair[0] not in (0x08, 0x10)]


ECC_CURVE_OIDS = {  # to enum FXK_ECC_CURVE_ID
    '1.2.840.10045.3.1.1': 0,  # prime192v1
    '1.3.132.0.33 ': 1,  # secp224r1
    '1.2.840.10045.3.1.7': 2,  # prime256v1
    '1.3.132.0.34': 3,  # secp384r1
    '1.3.132.0.35': 4,  # secp521r1
    '1.3.36.3.3.2.8.1.1.1': 5,  # brainpoolP160r1
    '1.3.36.3.3.2.8.1.1.3': 6,  # brainpoolP192r1
    '1.3.36.3.3.2.8.1.1.5': 7,  # brainpoolP224r1
    '1.3.36.3.3.2.8.1.1.7': 8,  # brainpoolP256r1
    '1.3.36.3.3.2.8.1.1.9': 9,  # brainpoolP320r1
    '1.3.36.3.3.2.8.1.1.11': 10,  # brainpoolP384r1
    '1.3.36.3.3.2.8.1.1.13': 11,  # brainpoolP512r1
    '1.3.101.112': 12,  # edwards25519
}

ECC_CURVE_NAMES = {  # openssl names
    'prime192v1': '1.2.840.10045.3.1.1',
    'secp224r1': '1.3.132.0.33',
    'prime256v1': '1.2.840.10045.3.1.7',
    'secp384r1': '1.3.132.0.34',
    'secp521r1': '1.3.132.0.35',
    'brainpoolP160r1': '1.3.36.3.3.2.8.1.1.1',
    'brainpoolP192r1': '1.3.36.3.3.2.8.1.1.3',
    'brainpoolP224r1': '1.3.36.3.3.2.8.1.1.5',
    'brainpoolP256r1': '1.3.36.3.3.2.8.1.1.7',
    'brainpoolP320r1': '1.3.36.3.3.2.8.1.1.9',
    'brainpoolP384r1': '1.3.36.3.3.2.8.1.1.11',
    'brainpoolP512r1': '1.3.36.3.3.2.8.1.1.13',
    'edwards25519': '1.3.101.112',
}


FXK_CIPHER_MODES = {
    'Proprietary': None,
    'ECB': 0,
    'CBC': 1,
    'KWP': 10,
}


PADDING_MODES = {
    'None':    0,
    'PKCS #1': 1,
    'PKCS #7': 1,
    'Bit':     2,
    'Zero':    3,
    'OEAP':    4,
}

PKI_KEY_USAGE_TYPE = [
    'critical', 'digitalSignature', 'nonRepudiation', 'keyEncipherment',
    'dataEncipherment', 'keyAgreement', 'keyCertSign', 'cRLSign',
    'encipherOnly', 'decipherOnly'
]
