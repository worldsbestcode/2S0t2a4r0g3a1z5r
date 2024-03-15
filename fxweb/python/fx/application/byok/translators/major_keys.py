"""
@file      byok/translators/major_keys.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2022

@section DESCRIPTION
Conversion functions for major keys
"""

from datetime import datetime
from typing import List, Optional

from lib.utils.data_structures import ExcryptMessage

import byok.models.keys as keys_models
import byok.models.major_keys as models
from byok import ByokTranslator
from byok.byok_enums import MAJOR_KEY_CONSTS, MAJOR_KEY_CONSTS_REVERSED, GPKIKeyType


class GDKM_major_keys_status(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str) -> List[ExcryptMessage]:
        skey_req = ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'get-major-key-status',
            'SI': sessionId,
        })
        skey_vmk_available = ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'get-major-key-status',
            'SI': sessionId,
            'FS': MAJOR_KEY_CONSTS_REVERSED['VMK'],
        })
        skey_ftk_available = ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'get-major-key-status',
            'SI': sessionId,
            'FS': MAJOR_KEY_CONSTS_REVERSED['FTK'],
        })
        vpkd_reqs = [
            ExcryptMessage({
                'AO': 'GDKM',
                'OP': 'read-cskl-session',
                'SI': sessionId,
                'ID': major_key_name,
            })
            for major_key_name in MAJOR_KEY_CONSTS_REVERSED
        ]

        return [skey_req, skey_vmk_available, skey_ftk_available, *vpkd_reqs]

    @staticmethod
    def parse(responses: List[ExcryptMessage]) -> models.MajorKeysInfo:
        skey_rsp, vmk_rsp, ftk_rsp, *vpkd_rsps = responses

        # FU tag present indicates that major key is available, otherwise VALUE OUT OF RANGE
        major_keys_available = [*MAJOR_KEY_CONSTS.values()]
        if not vmk_rsp.get('FU'):
            major_keys_available.remove('VMK')
        if not ftk_rsp.get('FU'):
            major_keys_available.remove('FTK')

        keys = {
            name: models.MajorKeyDetailedStatus(
                name=name,
                loaded=False,
                kcv=None,
                sessionInfo=None,
                type=None,
            )
            for name in major_keys_available
        }

        for name, vpkd in zip(major_keys_available, vpkd_rsps):
            if vpkd and vpkd.getFieldAsBool('ST'):
                keys[name].type = GPKIKeyType.values_to_names.get(vpkd['CT'])
                keys[name].sessionInfo = models.SessionInfo(
                    have=int(vpkd['KN']),
                    want=int(vpkd['KP']),
                    uploaders=vpkd['DA'].split(','),
                    expiration=datetime.strptime(vpkd['AF'], r'%Y-%m-%d %H:%M:%S'),
                    type='Fragments' if vpkd.getFieldAsBool('KT') else 'Components',
                )

        types = iter(skey_rsp['AF'].split(':'))
        for name, typ in zip(types, types):  # step by 2
            keys[name].type = GPKIKeyType.private_to_name.get(typ)

        kcvs = iter(skey_rsp['AE'].split(':')) # PMK:abba:MFK:daba
        for name, kcv in zip(kcvs, kcvs):
            keys[name].kcv = kcv
            keys[name].loaded = True

        return models.MajorKeysInfo(majorKeys=[*keys.values()])


class GDKM_delete_loaded_or_partial_major_key(ByokTranslator):
    # Delete both the existing major key of the given name and any partially loaded key with that ID
    @staticmethod
    def serialize(req: models.MajorKeyEraseIntent, sessionId: str, majorKey: str) -> Optional[List[ExcryptMessage]]:
        requests = []
        if req.clearLoaded:
            requests.append(GDKM_clear_major_key.serialize(sessionId=sessionId, majorKey=majorKey))
        if req.clearPartial:
            requests.append(GDKM_delete_cskl_session.serialize(sessionId=sessionId, majorKey=majorKey))
        return requests or None

    @staticmethod
    def parse(responses: List[ExcryptMessage]) -> None:
        pass


class GDKM_clear_major_key(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, majorKey: str) -> ExcryptMessage:
        request = ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'clear-major-key',
            'SI': sessionId,
            'BJ': MAJOR_KEY_CONSTS_REVERSED[majorKey],
        })
        return request

    @staticmethod
    def parse(*args):
        raise NotImplementedError


class GDKM_delete_cskl_session(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, majorKey: str) -> ExcryptMessage:
        request = ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'delete-cskl-session',
            'SI': sessionId,
            'ID': majorKey,
        })
        return request

    @staticmethod
    def parse(*args):
        pass


class GDKM_create_majorkey_fragments_initial(ByokTranslator):

    def serialize(self, req: models.GenerateMajorKeyFragmentsIntent, sessionId: str, majorKey: str) -> ExcryptMessage:
        self.req = req
        self.session_id = sessionId
        key_type = req.type or ('3TDES' if majorKey == 'MFK' else 'AES-256')
        request = ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-majorkey-fragments',
            'SI': sessionId,
            'AS': GPKIKeyType.names_to_values[key_type],
            'FS': MAJOR_KEY_CONSTS_REVERSED[majorKey],
            'BJ': req.m,
            'BO': req.n,
        })
        return request

    def parse(self, msg: ExcryptMessage):
        self.req._continuation_id = msg['CH']
        return (self.req, self.session_id)  # matches input to GDKM_create_majorkey_fragments


class GDKM_create_majorkey_fragments(ByokTranslator):
    @staticmethod
    def serialize(req: models.GenerateMajorKeyFragmentsIntent, sessionId: str) -> List[ExcryptMessage]:
        return [ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-majorkey-fragments-cont',
            'SI': sessionId,
            'CH': req._continuation_id,
            'BN': index,
        }) for index in range(1, req.n + 1)]

    @staticmethod
    def parse(msgs: List[ExcryptMessage]):
        return keys_models.KeyFragments(
            fragments=[
                keys_models.KeyFragment(fragment=msg['WA'], kcv=msg['XA'])
                for msg in msgs
            ],
            kcv=msgs[0]['AE']
        )


class GDKM_switch_major_key(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, majorKey: str) -> ExcryptMessage:
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'switch-major-key',
            'SI': sessionId,
            'FS': MAJOR_KEY_CONSTS_REVERSED[majorKey],
        })

    @staticmethod
    def parse(msg: ExcryptMessage):
        pass # just check for errors


class GDKM_randomize_major_key(ByokTranslator):
    @staticmethod
    def serialize(req: models.GenerateMajorKeyFragmentsIntent, sessionId: str, majorKey: str) -> ExcryptMessage:
        key_type = req.type or ('3TDES' if majorKey == 'MFK' else 'AES-256')
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'randomize-major-key',
            'SI': sessionId,
            'AS': GPKIKeyType.names_to_values[key_type],
            'FS': MAJOR_KEY_CONSTS_REVERSED[majorKey],
            'BJ': req.m,
            'BO': req.n,
        })

    @staticmethod
    def parse(msg: ExcryptMessage):
        return keys_models.KeyFragments(
            fragments=[
                keys_models.KeyFragment(fragment=fragment, kcv=kcv)
                for fragment, kcv in zip(msg['WA'].split(','), msg['XA'].split(','))
            ],
            kcv=msg['AE']
        )
