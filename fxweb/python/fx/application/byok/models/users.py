"""
@file      byok/models/users.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Resources and intents for role and identity management
"""

from typing import List, Optional
from datetime import datetime

from marshmallow.validate import Length

from byok import Model, field
from byok.models.auth import U2fChallengeDetails, U2fSignatureDetails
from byok.models.base import BasePaginationIntent, BasePaginationResponse
from byok.models.shared import Base64Str, IdentityRef, RoleRef, RoleType, U2fCredential


class RoleSummary(Model):
    name: RoleRef
    type: RoleType


class RoleList(BasePaginationResponse):
    roles: List[RoleSummary] = field()

    examples = {
        'Roles': {
            "nextPage": 1,
            "page": 1,
            "pageCount": 25,
            "roles": [{
                "name": "Anonymous",
                "type": "Application"
            }, {
                "name": "Crypto Operator",
                "type": "Application"
            }, {
                "name": "Administrator",
                "type": "Administration"
            }, {
                "name": "Single Admin",
                "type": "Administration"
            }],
            "totalItems": 4,
            "totalPages": 1
        }
    }



class IdentityListIntent(BasePaginationIntent):
    role: Optional[RoleRef] = field(description='Limit results to identities assigned given role')


class IdentitySummary(Model):
    name: IdentityRef
    type: RoleType
    manageable: bool = field(description='Identity is managed by the current role')
    locked: Optional[bool] = field(dump_default=None, description='Login for this identity is disabled')
    u2fEnabled: Optional[bool] = field(dump_default=None, description='Identity has U2F configured')


class IdentityList(BasePaginationResponse):
    identities: List[IdentitySummary] = field()

    examples = {
        'Identities': {
            "identities": [{
                "name": "Crypto1",
                "type": "Application"
            }, {
                "name": "Admin1",
                "type": "Administration"
            }, {
                "name": "Admin2",
                "type": "Administration"
            }],
            "nextPage": 1,
            "page": 1,
            "pageCount": 25,
            "totalItems": 3,
            "totalPages": 1
        },
        'Detailed results': {
            "identities": [{
                "name": "TestUser",
                "type": "Application",
                "locked": True,
                "u2fEnabled": False,
            }, {
                "name": "AppUser1",
                "type": "Application",
                "locked": False,
                "u2fEnabled": True,
            }],
            "nextPage": 1,
            "page": 1,
            "pageCount": 25,
            "totalItems": 2,
            "totalPages": 1
        }
    }


class Identity(Model):
    name: IdentityRef = field(example='Admin3')
    roles: List[RoleRef] = field(validate=Length(1), example=['Administrator'])
    locked: bool = field(description='Login for this identity is disabled', example=False)
    password: Base64Str = field(dump_default=None,
                                load_only=True,
                                example='aHVudGVyMg==',
                                validate=Length(4, 64))  # length of b64decoded raw bytes
    lastLogin: datetime = field(dump_default=None, dump_only=True)
    u2fCredentials: List[U2fCredential] = field(dump_default=None, description='Registered tokens',
                                                example=['FxToken16H'], dump_only=True)


class IdentityModify(Identity, schema_args={'partial': True}):
    pass  # Make all fields optional for PUT


class U2fCredentialList(Model):
    identity: IdentityRef
    u2fCredentials: List[U2fCredential]


class ChangePasswordIntent(Model):
    password: Base64Str = field(example='aHVudGVyMg==', validate=Length(4, 64))  # Length of raw bytes
    oldPassword: Base64Str = field(required=False, example='c2FmZXN0', validate=Length(4, 64), dump_default=None)


class U2fRegisterIntent(Model):
    data: Optional[List[U2fSignatureDetails]]


class U2fRegisterResponse(Model):
    data: Optional[List[U2fChallengeDetails]]
    userId: Optional[str]
