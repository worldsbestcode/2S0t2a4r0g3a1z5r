"""
@file      byok/models/auth.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Resources and intents for login
"""

from typing import Union, List

from marshmallow.validate import OneOf

from byok import Model, field
from .shared import Base64Str


class PkiChallengeCredentials(Model):
    """Credentials for initial request for PKI nonce authentication to receive a challenge nonce"""
    certData: Union[Base64Str, List[Base64Str]] = field(description='Base64-encoded client certificate with which to authenticate. Intermediate certificates for trust chaining may also be passed in ascending order.')


class PkiSignatureCredentials(Model):
    """Credentials for second request for PKI nonce authentication to send a signed nonce"""
    signature: Base64Str = field(description='Base64-encoded signature of the SHA-256 digest of the challenge using the private key associated with the client certificate.')


class UserPassCredentials(Model):
    """Credentials for username/password authentication"""
    username: str = field(example='Admin1')
    password: Base64Str = field(example='c2FmZXN0')


class U2fChallengeDetails(Model):
    """A single U2F challenge"""
    memqueueId: int
    challenge: str


class U2fSignatureDetails(Model):
    """A single U2F challenge response"""
    memqueueId: int
    attestation: str


class U2fSignatureCredentials(Model):
    """Credentials for U2F authentication"""
    username: str
    data: List[U2fSignatureDetails]


class JwtCredentials(Model):
    """Credentials for JWT authentication"""
    token: str


class LoginIntent(Model):
    """Base intent for all login methods"""
    _discriminator = {
        'propertyName': 'authType',
        'mapping': {
            'pkiChallenge': PkiChallengeCredentials,
            'pkiSignature': PkiSignatureCredentials,
            'userpass': UserPassCredentials,
            'jwt': JwtCredentials,
        }
    }
    authCredentials: Union[PkiChallengeCredentials, PkiSignatureCredentials, UserPassCredentials,
                           JwtCredentials] = field(discriminator=_discriminator)
    authType: str = field(validate=OneOf(_discriminator['mapping']))

    examples = {
        'Userpass': {
            'summary': 'Login as Admin1',
            'value': {
                'authType': 'userpass',
                'authCredentials': {
                    'username': 'Admin1',
                    'password': 'c2FmZXN0'
                }
            }
        },
        'Challenge': {
            'summary': 'Request a challenge nonce',
            'value': {
                'authType': 'pkiChallenge',
                'authCredentials': {
                    'certData': 'MIIDDjCCAfY...'
                }
            }
        },
        'Signature': {
            'summary': 'Submit a nonce signature',
            'value': {
                'authType': 'pkiSignature',
                'authCredentials': {
                    'signature': 'Mr75P7Pp22b...'
                }
            }
        },
        'JWT': {
            'summary': 'Login with JWT',
            'value': {
                'authType': 'jwt',
                'authCredentials': {
                    'token': 'eyJhbGciOiJIUzI...'
                }
            }
        }
    }


class PkiChallengeResponse(Model):
    """Server response for PKI nonce request"""
    challenge: Base64Str = field(attribute='pki_challenge_nonce')
    identityProvider: str = field(attribute='pki_provider')


class LoginCompleteResponse(Model):
    """Server response for completed login"""
    authorizedGroups: List[str] = field(attribute='authorized_groups')


class LoginIntentResponse(Model):
    """Server response for successful authentication requests"""
    response: Union[PkiChallengeResponse, LoginCompleteResponse]

    examples = {
        'Receive a challenge nonce': {
            'value': {
                'challenge': 'X1AharoVd+4gNNGNzU77F3kTj9f71ZnR39ESXboMwWI=',
                'identityProvider': 'PKI Provider'
            }
        },
    }
