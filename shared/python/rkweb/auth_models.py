"""
Copyright Futurex LP
Credits Lilith Neathery
"""

from typing import Union, List

from marshmallow import fields
from marshmallow.validate import OneOf

from rkweb.lilmodels.base import Model, field
from rkweb.lilmodels.shared import Base64Str


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
    multiLogin: bool = field(
        example=False,
        description="Want to login multiple users",
        load_default=True,
        dump_default=True)


class FidoChallengeResponse(Model):
    """Complete dual-factor login using FIDO token"""
    response: Base64Str = field(description="Answer to FIDO challenge")

class OneTimePassword(Model):
    """Complete dual-factor login using OTP"""
    password: str = field(description="One time password")


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
            'fido': FidoChallengeResponse,
            'otp': OneTimePassword,
        }
    }
    authCredentials: Union[PkiChallengeCredentials, PkiSignatureCredentials, UserPassCredentials,
                           JwtCredentials, FidoChallengeResponse, OneTimePassword] = field(discriminator=_discriminator)
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


class DfChallengeResponse(Model):
    required: bool = field(description="If dual-factor is optional")
    method: str = field(description="Dual-factor type (Ex: FIDO, OTP)")
    nonce: Base64Str = field(description="Challenge value to sign")
    credential: str = field(description="Name of credential expected")


class LoginResponseRole(Model):
    id: int = field(description="Role ID")
    uuid: str = field(description="Role UUID")
    name: str = field(description="Role name")
    principal: bool = field(description="Whether or not the role is a principal role")


class LoginResponseManagedRole(Model):
    id: int = field(description="Role ID")
    uuid: str = field(description="Role UUID")
    type: str = field(description="Managed role type",
        validate=OneOf(["Controllable", "Assignable", "Viewable"]),
    )

class UserInfo(Model):
    id: int = field(description="Internal user identifier")
    # TODO: uuid
    name: str = field(description="Username")
    expired: bool = field(description="Whether the user logged in with an expired credential")
    defaultPw: bool = field(description="Whether the user logged in with a default password")

class LoginCompleteResponse(Model):
    users: List[UserInfo] = field(description="Logged in users")
    perms: List[str] = field(description="Permission strings")
    authPerms: List[str] = field(description="Permission strings derived from authorized roles (not anonymous perms)")
    roles: List[LoginResponseRole] = field(description="Logged in roles")
    managedRoles: List[LoginResponseManagedRole] = field(description="Roles that this role manages")

    hardened: bool = field(description="If the logged in users are HSM users")
    management: bool = field(description="If the logged in users are management or application users")
    userManagement: bool = field(description="If the logged in users are restricted to user management")
    fullyLoggedIn: bool = field(description="If the login session is complete")

    token: str = field(description="JWT authorization token")
    tokenExpiration: str = field(description="JWT expiration (format %Y-%m-%d %H:%M:%S)")

    dualFactor: DfChallengeResponse = field(description="Dual-factor login information if requested")

    hasPrincipal: bool = field(description="If at least one principal role has logged in")
    remainingLogins: int = field(description="The most number of remaining logins possible")


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
