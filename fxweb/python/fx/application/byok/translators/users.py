"""
@file      byok/translators/users.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Conversion functions for role and identity management
"""

from datetime import datetime
from typing import List

from lib.utils.data_structures import ExcryptMessage

import byok.models.users as models
from byok import ByokTranslator
from byok.models.base import BasePaginationIntent


def nonempty_split(value: str) -> List[str]:
    if value:
        return value.split(',')
    return []


class GDGD_list_roles(ByokTranslator):
    @staticmethod
    def serialize(obj: BasePaginationIntent, sessionId: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDGD'
        msg['OP'] = 'list-roles'
        msg['SI'] = sessionId
        msg['PG'] = obj.page - 1  # API pages start at 1, GDGD chunks start at 0
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.RoleList:
        prods = msg['NA'].split(',')
        admins = msg['NB'].split(',')
        total_pages = int(msg['TO'])

        roles = [
            models.RoleSummary(name, typ)
            for names, typ in ((prods, 'Application'), (admins, 'Administration'))
            for name in names if name
        ]

        rsp = models.RoleList(roles=roles)
        rsp.totalPages = total_pages
        return rsp


class GDGD_list_identities(ByokTranslator):
    @staticmethod
    def serialize(obj: models.IdentityListIntent, sessionId: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDGD'
        msg['OP'] = 'list-identities'
        msg['SI'] = sessionId
        msg['SP'] = 1  # Split results into AD (prod) and PR (admin) tags
        msg['PG'] = obj.page - 1  # API pages start at 1, GDGD chunks start at 0
        msg['NA'] = obj.role or None
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.IdentityList:
        if not msg.success:
            return models.IdentityList(identities=[])

        prods = msg['PR'].split(',')
        admins = msg['AD'].split(',')
        total_pages = int(msg['TO'])

        identities = [
            models.IdentitySummary(name=name, type=typ, manageable=True)
            for names, typ in ((prods, 'Application'), (admins, 'Administration'))
            for name in names if name
        ]
        rsp = models.IdentityList(identities=identities)
        rsp.totalPages = total_pages
        return rsp


class GDGD_create_identity(ByokTranslator):
    @staticmethod
    def serialize(obj: models.Identity, sessionId: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDGD'
        msg['OP'] = 'create-identity'
        msg['SI'] = sessionId
        msg['NA'] = obj.name
        msg['RO'] = ','.join(obj.roles)
        msg['PW'] = obj.password.hex() if obj.password else None
        msg['LO'] = int(obj.locked)
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> None:
        pass


class GDGD_read_identity(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, identity: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDGD'
        msg['OP'] = 'read-identity'
        msg['SI'] = sessionId
        msg['NA'] = identity
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.Identity:
        return models.Identity(
            name=msg['NA'],
            roles=nonempty_split(msg['RO']),
            locked=msg['LO'] == '1',
            lastLogin=datetime.strptime(msg['LL'], '%Y-%m-%d %H:%M:%S'),
            u2fCredentials=nonempty_split(msg.get('UC', '')),
        )


class GDGD_update_identity(ByokTranslator):
    @staticmethod
    def serialize(obj: models.Identity, sessionId: str, identity: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDGD'
        msg['OP'] = 'update-identity'
        msg['SI'] = sessionId
        msg['NA'] = identity
        msg['NB'] = obj.name
        msg['RO'] = ','.join(obj.roles)
        msg['PW'] = obj.password.hex() if obj.password else None
        msg['LO'] = int(obj.locked)
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> None:
        pass


class GDGD_delete_identity(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, identity: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDGD'
        msg['OP'] = 'delete-identity'
        msg['SI'] = sessionId
        msg['NA'] = identity
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> None:
        pass


class GDGD_change_password(ByokTranslator):
    @staticmethod
    def serialize(obj: models.ChangePasswordIntent, sessionId: str, identity: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        if obj.oldPassword:
            msg['AO'] = 'GDGD'
            msg['OP'] = 'change-password'
            msg['SI'] = sessionId
            msg['DA'] = identity
            msg['PW'] = obj.oldPassword.hex()
            msg['PX'] = obj.password.hex()
        else:
            msg['AO'] = 'GDGD'
            msg['OP'] = 'update-identity'
            msg['SI'] = sessionId
            msg['NA'] = identity
            msg['PW'] = obj.password.hex()
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> None:
        pass


class GDGD_read_u2f(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, identity: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDGD'
        msg['OP'] = 'read-u2f'
        msg['SI'] = sessionId
        msg['DA'] = identity
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.U2fCredentialList:
        return models.U2fCredentialList(
            identity=msg.get('DA', ''),
            u2fCredentials=nonempty_split(msg.get('UC', '')),
        )


class GDGD_register_u2f(ByokTranslator):

    def serialize(self, req: models.U2fRegisterIntent, sessionId: str, identity: str, name: str) -> ExcryptMessage:
        if not req.data:
            return self.serialize_step_1(sessionId=sessionId, identity=identity, name=name)
        return self.serialize_step_2(req.data, sessionId=sessionId)

    def serialize_step_1(self, sessionId: str, identity: str, name: str):
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'register-u2f-challenge',
            'SI': sessionId,
            'DA': identity,
            'NA': name,
            'WC': 0,  # NOT web credential
        })

    def serialize_step_2(self, signatures: List[models.U2fSignatureDetails], sessionId: str):
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'register-u2f-signature',
            'SI': sessionId,
            'CH': ','.join(str(pair.memqueueId) for pair in signatures),
            'BO': ','.join(pair.attestation for pair in signatures),
        })

    def parse(self, msg: ExcryptMessage) -> models.U2fRegisterResponse:
        challenges = None
        if msg.get('CN') == 'C':  # "challenge" step
            challenges = [
                models.U2fChallengeDetails(memqueueId=int(mqid), challenge=nonce)
                for mqid, nonce in zip(msg['CH'].split(','), msg['CL'].split(','))
            ]
        return models.U2fRegisterResponse(data=challenges, userId=msg.get('UI', None))


class GDGD_delete_u2f(ByokTranslator):

    def serialize(self, sessionId: str, identity: str, name: str) -> ExcryptMessage:
        return ExcryptMessage({
            'AO': 'GDGD',
            'OP': 'delete-u2f',
            'SI': sessionId,
            'DA': identity,
            'NA': name or None,
            'DD': name is None,
        })

    def parse(self, msg: ExcryptMessage) -> None:
        pass  # nothing to do, just check for errors
