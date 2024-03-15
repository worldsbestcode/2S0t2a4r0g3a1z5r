"""
@file      byok/translators/cskl.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2022

@section DESCRIPTION
Conversion functions for partial key loading
"""

from lib.utils.data_structures import ExcryptMessage

import byok.models.cskl as models
from byok import ByokTranslator
from byok.byok_enums import MAJOR_KEY_CONSTS_REVERSED, GPKIKeyType
from byok.utils.key_blocks import to_hex
from byok.utils.key_table import fw_multi_sec_usage_from_name, fw_sym_key_usage_from_name


class GDKM_create_ephemeral_key(ByokTranslator):
    @staticmethod
    def serialize(obj: models.CreateKeyLoadSessionIntent, sessionId: str) -> ExcryptMessage:
        request = ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-ephemeral-key',
            'SI': sessionId,
            'RD': obj.clearPublicKeyBlock,
            'AS': 0,  # KEK
            'CZ': 'B',  # Wrap/Unwrap (aka Encrypt/Decrypt)
            'TF': not obj.majorKeyLoad,  # 1=main card only (CPKD), 0=session for all devices (HPKD)
        })
        return request

    @staticmethod
    def parse(rsp: ExcryptMessage) -> models.KeyLoadSessionDetails:
        return models.KeyLoadSessionDetails(
            sessions=[
                models.CSKLSession(memqueueId=int(id_), ephemeralKey=key)
                for id_, key in zip(rsp['CH'].split(','), rsp['BG'].split(','))
            ]
        )


class GDKM_hpkd(ByokTranslator):
    @staticmethod
    def serialize(obj: models.HPKDLoadData, sessionId: str, majorKey: str, vpkd: models._VpkdInternal) -> ExcryptMessage:

        fragment = obj.input.fragment if isinstance(obj.input, models.FragmentUploadDetails) else None
        components = not fragment and [device.component for device in obj.input]

        if vpkd.memqueueIdList and components:
            op = 'add-cskl-mk-component'
        elif vpkd.memqueueIdList and fragment:
            op = 'add-cskl-mk-fragment'
        elif components:
            op = 'create-cskl-session-from-mk-component'
        else:
            op = 'create-cskl-session-from-mk-fragment'

        key_type = obj.type or vpkd.keyType or ('3TDES' if majorKey == 'MFK' else 'AES-256')

        request = ExcryptMessage({
            'AO': 'GDKM',
            'OP': op,
            'SI': sessionId,
            'MK': MAJOR_KEY_CONSTS_REVERSED[majorKey],
            'ID': majorKey,  # using major key as the unique memqueue name
            'CT': GPKIKeyType.names_to_values[key_type],
            'EC': obj.input.encrypted if fragment else 1,  # components always wrapped
            'CH': ','.join(str(device.memqueueId) for device in obj.input) if components else None,
            'CS': ','.join(vpkd.memqueueIdList) if vpkd.memqueueIdList else None,
            'AK': ','.join(components) if components else None,
            'BO': fragment,
            'KP': vpkd.numComponents or obj.numComponents,  # ignored if fragments
            'TF': 0,  # always broadcast
        })
        return request

    @staticmethod
    def parse(rsp: ExcryptMessage) -> models.PartialKeyLoadResponse:
        return models.PartialKeyLoadResponse(
            partKcv=rsp.get('AE', ''),
            have=rsp.get('KN'),
            want=rsp.get('KP'),
            authReceipt=None,
            kcv=None,
        )


class GDKM_read_cskl_session(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, majorKey: str) -> ExcryptMessage:
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'read-cskl-session',
            'SI': sessionId,
            'ID': majorKey,
        })

    @staticmethod
    def parse(rsp: ExcryptMessage) -> models._VpkdInternal:
        memqueueIdList = [*filter(None, rsp.get('CH', '').split(','))] or None
        numComponents = int(rsp.get('KP', 0))
        key_type = GPKIKeyType.values_to_names.get(rsp.get('CT'), None)
        return models._VpkdInternal(
            memqueueIdList=memqueueIdList,
            numComponents=numComponents,
            keyType=key_type,
        )


class GDKM_create_cskl_receipt(ByokTranslator):
    @staticmethod
    def serialize(obj: models.CPKDLoadData, sessionId: str) -> ExcryptMessage:
        request = ExcryptMessage({
            'AO': 'GDKM',
            'SI': sessionId,
            'CT': GPKIKeyType.names_to_values[obj.type],
            'FS': MAJOR_KEY_CONSTS_REVERSED[obj.majorKey],
            'AS': to_hex(obj.modifier),
            'CZ': fw_sym_key_usage_from_name(obj.usage),
            'SF': fw_multi_sec_usage_from_name(obj.securityUsage),
            'KP': obj.numComponents,
            'TF': 1,  # for auth receipts only need to access the main card
        })
        if isinstance(obj.input, models.ComponentUploadDetails):
            request['OP'] = 'create-cskl-receipt-from-component'
            request['EC'] = 1  # component is wrapped
            request['AK'] = obj.input.component
            request['CH'] = obj.input.memqueueId
        else:
            request['OP'] = 'create-cskl-receipt-from-fragment'
            request['EC'] = obj.input.encrypted
            request['BO'] = obj.input.fragment

        return request

    @staticmethod
    def parse(rsp: ExcryptMessage) -> models.PartialKeyLoadResponse:
        return models.PartialKeyLoadResponse(
            partKcv=rsp.get('AE', ''),
            authReceipt=rsp.get('BO', ''),
            have=rsp.get('KN'),
            want=rsp.get('KP'),
            kcv=None,
        )


class GDKM_finalize_hpkd(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, vpkd: models._VpkdInternal) -> ExcryptMessage:
        assert vpkd.memqueueIdList
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'finalize-cskl-mk-session',
            'SI': sessionId,
            'TF': 0,  # after HPKD we want to broadcast to all hsms in the device group
            'CS': ','.join(vpkd.memqueueIdList)
        })

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.KeyChecksum:
        return msg.get('AE', '')
