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

from datetime import datetime
from typing import List, Optional

from marshmallow.validate import OneOf, Range

from byok import Model, field
from byok.byok_enums import MAJOR_KEY_CONSTS
from byok.models.base import NewType
from byok.models.shared import KeyChecksum, SymmetricKeyType

AllMajorKeys = NewType('Major Key', str, validate=OneOf(MAJOR_KEY_CONSTS.values()))


class SessionInfo(Model):
    have: int
    want: int
    uploaders: List[str]
    expiration: datetime
    type: str = field(validate=OneOf(('Components', 'Fragments')))


class MajorKeyDetailedStatus(Model):
    # if loaded:
    kcv: Optional[KeyChecksum]

    # if session:
    sessionInfo: Optional[SessionInfo]

    # if loaded or session:
    type: Optional[SymmetricKeyType]

    # always:
    name: AllMajorKeys
    loaded: bool


class MajorKeysInfo(Model):
    majorKeys: List[MajorKeyDetailedStatus]


class MajorKeyEraseIntent(Model):
    clearLoaded: bool = field(dump_default=True, description='Erase major key')
    clearPartial: bool = field(dump_default=True, description='Erase key load session for major key')


class GenerateMajorKeyFragmentsIntent(Model):
    type: Optional[SymmetricKeyType]
    m: int = field(description='Minimum fragments to reassemble key', validate=Range(2, 12))
    n: int = field(description='Total fragments to generate', validate=Range(2, 24))

    _continuation_id: str = field(hidden=True, dump_only=True, dump_default=None)
