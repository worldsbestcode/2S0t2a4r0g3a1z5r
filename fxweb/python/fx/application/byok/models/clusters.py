"""
@file      byok/models/clusters.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Resources and intents for device groups
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

from marshmallow.validate import OneOf

from byok import Model, field
from byok.models.auth import U2fChallengeDetails, U2fSignatureCredentials, UserPassCredentials
from byok.models.shared import IdentityRef, RoleRef, Permission, UUID, U2fCredential


class DeviceGroupSummary(Model):
    name: str
    id: UUID
    enabled: bool
    deviceType: str
    deviceCount: int


class DeviceGroupList(Model):
    groups: List[DeviceGroupSummary]

    examples = {
        'List': {
            'groups': [
                {
                    'deviceType': 'HSM',
                    'enabled': False,
                    'id': '{01641502-1B3A-0001-000C-02F737BCF0C2}',
                    'name': 'HSM Group 1',
                    'deviceCount': 2,
                }
            ]
        }
    }


class DeviceGroup(DeviceGroupSummary):
    description: str
    ports: Dict[str, int]
    attributes: Dict[str, str]
    features: Optional[List[str]]

    examples = {
        'Example device group': {
            'attributes': {},
            'description': 'VHSM Cluster #2',
            'deviceType': 'HSM',
            'enabled': True,
            'features': ['AES', 'FINANCIALWITHGP', 'RSA', 'ECC', '...'],
            'id': '{01AF0560-1B3A-0001-0016-219F16D1C321}',
            'name': 'us-east',
            'deviceCount': 2,
            'ports': {
                'Production': 9001
            },
        }
    }


class Session(Model):
    group: UUID = field(description='Device Group UUID', dump_default=None)
    id: UUID = field(dump_only=True, description='Session UUID', dump_default=None)


class SessionList(Model):
    sessions: List[Session] = field(description='List of open sessions')


class ClusterLoginIntent(Model):
    authCredentials: Union[U2fSignatureCredentials, UserPassCredentials]
    authType: str = field(validate=OneOf(('userpass', 'u2f')))


class ClusterAuthorizationState(Model):
    loginComplete: bool
    permissions: List[Permission]
    roles: List[RoleRef]
    identities: List[IdentityRef]
    passwordExpiration: Optional[datetime]
    u2fChallenge: Optional[List[U2fChallengeDetails]]
    u2fCredentials: Optional[List[List[U2fCredential]]]

    examples = {
        'Anonymous': {
            'identities': [],
            'loginComplete': False,
            'permissions': [
                'Excrypt',
                'Excrypt:ECHO',
                'Keys',
                'Keys:All Slots',
                'Standard Cmd',
                'Standard Cmd:00',
                'Standard Cmd:01'
            ],
            'roles': [
                'Anonymous'
            ]
        }
    }


class FeaturesDump(Model):
    features: List[str]


class SettingsDump(Model):
    settings: dict
