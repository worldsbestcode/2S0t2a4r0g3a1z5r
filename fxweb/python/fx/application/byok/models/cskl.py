"""
@file      byok/models/major_keys.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2022

@section DESCRIPTION
Resources and intents for major key management
"""

from typing import List, Optional, Union
from marshmallow import ValidationError, validates_schema

from marshmallow.validate import Length, OneOf, Range

from byok import Model, field
from byok.byok_enums import MAJOR_KEY_CONSTS
from byok.models.base import NewType
from byok.models.shared import (KeyBlockStr, KeyChecksum, KeyModifier, KeyMultiSecUsage,
                                MajorKey, SymKeyMultiUsage, SymmetricKeyType)

AllMajorKeys = NewType('Major Key', str, validate=OneOf(MAJOR_KEY_CONSTS.values()))


class _VpkdInternal(Model):
    # Not user-facing, just to pass around a parsed VPKD response
    memqueueIdList: Optional[List[str]]  # CS tag, could be None if no session
    numComponents: int  # KP tag, could be 0 if no session
    keyType: SymmetricKeyType  # CT tag, could be None


class CreateKeyLoadSessionIntent(Model):
    clearPublicKeyBlock: KeyBlockStr  # hex DER
    majorKeyLoad: bool = field(description='Create session for each device in the cluster (for major key load)')


class CSKLSession(Model):
    memqueueId: int
    ephemeralKey: KeyBlockStr


class KeyLoadSessionDetails(Model):
    sessions: List[CSKLSession]


class ComponentUploadDetails(Model):
    memqueueId: int
    component: str


class FragmentUploadDetails(Model):
    fragment: str = field(validate=Length(min=1))
    encrypted: bool = field(description='Encrypt fragments under remote SCEK', dump_default=False)


class CPKDLoadData(Model):
    type: SymmetricKeyType
    modifier: KeyModifier
    usage: SymKeyMultiUsage
    numComponents: Optional[int] = field(validate=Range(min=1, max=12))
    securityUsage: KeyMultiSecUsage = field(default_factory=list)
    input: Union[ComponentUploadDetails, FragmentUploadDetails] = field(description='Key part to create auth receipt with')
    majorKey: MajorKey = field(dump_default='PMK', description='Major key that the final key will be under')

    @validates_schema
    def _components_implies_num_parts(_, data, **kwargs):
        is_component = isinstance(data.get('input'), ComponentUploadDetails)
        num_components = data.get('numComponents')
        if is_component and not num_components:
            raise ValidationError('Field is required if components given', 'numComponents')


class HPKDLoadData(Model):
    type: Optional[SymmetricKeyType]
    input: Union[List[ComponentUploadDetails], FragmentUploadDetails]
    numComponents: Optional[int] = field(description='Total number of components', validate=Range(min=1, max=12))

    @validates_schema
    def _non_empty_component_list(self, data, **kwargs):
        is_fragment = isinstance(data.get('input'), FragmentUploadDetails)
        if not is_fragment and not data.get('input'):
            raise ValidationError('Shorter than minimum length 1', 'input')

    @validates_schema
    def _components_implies_num_parts(_, data, **kwargs):
        is_component = isinstance(data.get('input'), ComponentUploadDetails)
        num_components = data.get('numComponents')
        if is_component and not num_components:
            raise ValidationError('Field is required if components given', 'numComponents')


class PartialKeyLoadResponse(Model):
    partKcv: KeyChecksum = field(description='Checksum of uploaded part')
    authReceipt: Optional[str] = field(description='Approved partial key data')
    have: Optional[int] = field(description='Total parts uploaded')
    want: Optional[int] = field(description='Total parts needed')
    kcv: Optional[KeyChecksum] = field(description='Checksum of loaded key')
