"""
@file      byok/translators/clusters.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Conversion functions for device groups
"""

import base64
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

from lib.utils.data_structures import ExcryptMessage
from lib.utils.string_utils import from_hex

from byok import ByokTranslator
import byok.models.clusters as models


class GDLB_list(ByokTranslator):
    @staticmethod
    def serialize() -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDLB'
        msg['OP'] = 'list'
        msg['CT'] = '1'  # Also get deviceCount
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.DeviceGroupList:
        # rk doesn't send tags if there aren't any viewable groups
        if 'NA' not in msg:
            return models.DeviceGroupList(groups=[])

        groups = []
        for (
                id_,
                name,
                enabled,
                num_devices,
                device_type,
        ) in zip(
                msg['ID'].split(','),
                msg['NA'][1:-1].split("','"),
                msg['EN'].split(','),
                msg['CT'].split(','),
                msg['GV'].split(','),
        ):
            groups.append(models.DeviceGroupSummary(
                id=id_,
                name=name,
                enabled=enabled,
                deviceCount=num_devices,
                deviceType=device_type,
            ))

        return models.DeviceGroupList(groups=groups)


class GDLB_get(ByokTranslator):
    @staticmethod
    def serialize(groupId: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDGS'
        msg['ID'] = groupId
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.DeviceGroup:
        return models.DeviceGroup(
            id=msg['ID'],
            name=msg['GE'],
            ports=GDLB_get.parse_ports(msg['LP']),
            enabled=msg['SA'] == 'Running',
            deviceCount=msg['DC'],
            deviceType=msg['TY'],
            attributes=GDLB_get.parse_attrs(msg['KV']),
            description=msg['GH'],
            features=None,
        )

    @staticmethod
    def parse_ports(lp: str) -> Dict[str, int]:
        return dict((k, int(v)) for kv in lp.split(',') if kv for k, v in (kv.split(':'),) if int(v) > 0)

    @staticmethod
    def parse_attrs(attrs: str) -> Dict[str, str]:
        return dict((k, v) for kv in from_hex(attrs).split(',') if kv for k, v in (kv.split(':'),))


class GDGD_connect(ByokTranslator):
    def serialize(self, obj: models.Session) -> ExcryptMessage:
        self.group = obj.group
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'connect',
            'GI': obj.group,
        })

    def parse(self, msg: ExcryptMessage) -> models.Session:
        return models.Session(id=msg['SI'], group=self.group)


class GDGD_list_sessions(ByokTranslator):
    @staticmethod
    def serialize() -> ExcryptMessage:
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'list-sessions',
        })

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.SessionList:
        sessions = []
        for pair in msg.get('SL', '').split(','):
            session_id, _, group_id = pair.partition(':')
            sessions.append(models.Session(group=group_id, id=session_id))
        return models.SessionList(sessions=sessions)


class GDGD_disconnect(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str) -> ExcryptMessage:
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'disconnect',
            'SI': sessionId,
        })

    @staticmethod
    def parse(msg: ExcryptMessage) -> None:
        pass


class GDGD_login_status(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str):
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'login-status',
            'SI': sessionId,
        })

    @staticmethod
    def parse(msg: ExcryptMessage):
        pw_expire_time = None
        if 'ET' in msg:
            pw_expire_time = timedelta(seconds=int(msg['ET'])) + datetime.utcnow()

        u2f_challenge = None
        u2f_credentials = None
        if msg.get('AI') == 'U2F':
            u2f_challenge = [
                models.U2fChallengeDetails(memqueueId=int(mqid), challenge=challenge)
                for mqid, challenge in zip(msg['TH'].split(','), msg['CL'].split(','))
            ]
            u2f_credentials = []
            for sub in [*filter(None, msg['UC'].split('|'))]:
                u2f_credentials.append([*filter(None, sub.split(','))])

        return models.ClusterAuthorizationState(
            roles=[*filter(None, msg['RO'].split(','))],
            identities=[*filter(None, msg['US'].split(','))],
            permissions=GDGD_login_status.parse_perms(msg['PR']),
            loginComplete=(msg['LC'] == 'Y'),
            passwordExpiration=pw_expire_time,
            u2fChallenge=u2f_challenge,
            u2fCredentials=u2f_credentials,
        )

    @staticmethod
    def parse_perms(perm_str: str) -> List[str]:
        result = []
        for category_and_value_list in perm_str.split(','):
            category, _, value_list = category_and_value_list.partition(':')
            result.append(category)
            result.extend(f'{category}:{value}' for value in value_list.split('|')
                          if value not in (category, ''))
        return result


class GDGD_login_pw(GDGD_login_status):
    @staticmethod
    def serialize(obj: models.UserPassCredentials, sessionId: str):
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'login-pw',
            'SI': sessionId,
            'DA': obj.username,
            'PW': obj.password.hex(),
        })


class GDGD_login_u2f(GDGD_login_status):
    @staticmethod
    def serialize(obj: models.U2fSignatureCredentials, sessionId: str):
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'login-u2f',
            'SI': sessionId,
            'DA': obj.username,
            'TH': ','.join(str(pair.memqueueId) for pair in obj.data),
            'BO': ','.join(str(pair.attestation) for pair in obj.data),
        })


class GDGD_logout(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str):
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'logout',
            'SI': sessionId,
        })

    @staticmethod
    def parse(msg: ExcryptMessage) -> None:
        pass


class GDGD_read_features(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str):
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'read-features',
            'SI': sessionId,
        })

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.FeaturesDump:
        return models.FeaturesDump(
            features=msg['BO'].split(','),
        )


class GDGD_get_settings(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, _continuation_ids: List[Optional[str]] = None):
        categories = (
            'configuration',
            'statistics',
            'features',
            'functionSettings',
            'keys',
            'loggingSettings',
            'networkSettings',
            'users',
            'virtual',
        )
        msgs = [ExcryptMessage(f'[AOGDGD;OPget-settings;SI{sessionId};SE{category};]') for category in categories]
        if _continuation_ids:
            for msg, cont_id in zip(msgs, _continuation_ids):
                if cont_id:
                    msg['CH'] = cont_id
            msgs = [msg if msg.get('CH') else None for msg in msgs]  # drop ones we already got the last chunk for
        return msgs

    @staticmethod
    def parse(msgs: List[ExcryptMessage]) -> models.SettingsDump:
        settings = {}
        for msg in msgs:
            msg = json.loads(base64.b64decode(msg['SE'].encode()))
            if not msg.get('error'):
                settings.update(msg)
        return models.SettingsDump(settings=settings)

    @staticmethod
    def combine(old_msgs, new_msgs):
        for old, new in zip(old_msgs, new_msgs):
            old.setdefault('SE', '')
            old['SE'] += (new and new.get('SE')) or ''

        if not old_msgs:
            old_msgs.extend(new_msgs)

        cont_ids = [msg and msg.get('CH') for msg in new_msgs]
        return any(cont_ids) and cont_ids

    def __call__(self, msg_sender, *args, **kwargs):
        combined_msgs = []
        cont_ids = []
        while True:
            req_msgs = self.serialize(*args, **kwargs, _continuation_ids=cont_ids)
            rsp_msgs = msg_sender(req_msgs)
            cont_ids = self.combine(combined_msgs, rsp_msgs)
            if not cont_ids:
                return self.parse(combined_msgs)
