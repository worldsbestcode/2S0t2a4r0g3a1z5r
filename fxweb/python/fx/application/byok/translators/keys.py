"""
@file      byok/translators/keys.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Conversion functions for keys
"""

from typing import Dict, List, Optional, Union, cast

from lib.utils.container_filters import first
from lib.utils.data_structures import ExcryptMessage
from lib.utils.fx_decorators import singledispatchmethod
from lib.utils.string_utils import hex_der_to_pem

import byok.models.keys as models
from byok import ByokTranslator
from byok.byok_enums import ECC_CURVE_NAMES, ECC_CURVE_OIDS, FXK_CIPHER_MODES, MAJOR_KEY_CONSTS_REVERSED, PADDING_MODES, GPKIKeyType
from byok.utils.key_blocks import parse_tr31_to_details, to_hex
from byok.utils.key_table import (KEY_TYPE_CONSTS, MAJOR_KEY_CONSTS, fw_asym_key_usage_from_name, fw_multi_key_usage_from_name,
    fw_multi_key_usage_to_name, fw_multi_sec_usage_from_name, fw_multi_sec_usage_to_name, fw_sym_key_usage_from_name)


class GDKM_read_keytable_counts(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str) -> List[ExcryptMessage]:
        # 3 messages: GPKI;FS0, GPKI;FS1, CONF;FS13
        requests = [
            ExcryptMessage({
                'AO': 'GDKM',
                'OP': 'read-keytable-info',
                'SI': sessionId,
                'FS': count_type,
            })
            for count_type in ('0', '1')
        ] + [
            ExcryptMessage({
                'AO': 'GDGD',
                'OP': 'read-features',
                'SI': sessionId,
            })
        ]
        return requests

    @staticmethod
    def parse(msgs: List[ExcryptMessage]) -> models.KeyTableSummary:
        fs_0, fs_1, features = msgs

        available = GDKM_read_keytable_counts.parse_key_info(fs_0['XB'])
        in_use = GDKM_read_keytable_counts.parse_key_info(fs_1['XB'])
        # If not a valid key type due to features, default to 0 available:
        for typ in range(1, 15):
            available.setdefault(typ, 0)
            in_use.setdefault(typ, 0)

        total_keys_in_use = sum(in_use.values())
        total_keys_available = int(fs_0['XC']) - total_keys_in_use
        symmetric_keys_in_use = sum(in_use[typ] for typ in range(1, 7))
        symmetric_keys_available = available[1]

        financial_mode = 'GP' not in features['BO'].split(',')

        Totals = models.KeyTableKeyTotal
        return models.KeyTableSummary(
            total=Totals(total_keys_available, total_keys_in_use),
            symmetric=Totals(symmetric_keys_available, symmetric_keys_in_use),
            diebold=Totals(available[7], in_use[7]),
            rsa512=Totals(available[8], in_use[8]),
            rsa1024=Totals(available[9], in_use[9]),
            rsa2048=Totals(available[10], in_use[10]),
            rsa3072=Totals(available[11], in_use[11]),
            rsa4096=Totals(available[12], in_use[12]),
            ecc=Totals(available[13], in_use[13]),
            certificate=Totals(available[14], in_use[14]),
            financial=financial_mode,
        )

    @staticmethod
    def parse_key_info(xb_tag: str) -> Dict[int, int]:
        return dict((int(k), int(v)) for kv in xb_tag.split(',') if kv for k, v in (kv.split(':'),))


class GDKM_load_key(ByokTranslator):
    def serialize(self, obj: models.KeySlotLoadIntent, sessionId: str, tableType: str = None, slot: int = None):
        source_auth_receipts = isinstance(obj.key, models.AuthReceipts)
        source_keyblock = isinstance(obj.key, models.KeyBlockLoad)
        source_diebold = isinstance(obj.key, models.DieboldTable)
        source_certificate = isinstance(obj.key, models.Certificate)
        source_random = not (source_auth_receipts or source_keyblock or source_diebold or source_certificate)

        if source_random:
            translator = GDKM_create_symmetric_key
            if isinstance(obj.key, models.RSAKeyDetails): translator = GDKM_create_rsa_key()
            elif isinstance(obj.key, models.ECCKeyDetails): translator = GDKM_create_ecc_key()
            self.parse = translator.parse
            return translator.serialize(obj.key, sessionId=sessionId, slot=slot)

        elif source_keyblock:
            translator = GDKM_import_symmetric_keyblock if getattr(obj.key, 'keyBlock') else GDKM_import_asymmetric_keyblock
            self.parse = translator.parse
            return translator.serialize(obj.key, sessionId=sessionId, slot=slot)

        elif source_auth_receipts:
            translator = GDKM_combine_auth_receipts_keyslot
            self.parse = translator.parse
            return translator.serialize(obj.key, sessionId=sessionId, slot=slot)

        elif source_diebold:
            self.parse = GDKM_import_diebold.parse
            return GDKM_import_diebold.serialize(obj.key, sessionId=sessionId, slot=slot)

        elif source_certificate:
            self.parse = GDKM_import_certificate.parse
            return GDKM_import_certificate.serialize(obj.key, sessionId=sessionId, slot=slot)

        raise NotImplementedError

    def parse(self, msg):
        raise NotImplementedError


class GDKM_generate_key_block(ByokTranslator):
    def serialize(self, obj: models.GenerateKeyBlockIntent, sessionId: str):
        if isinstance(obj.key, models.SymmetricKeyDetails):
            translator = GDKM_create_symmetric_key
        elif isinstance(obj.key, models.RSAKeyDetails):
            translator = GDKM_create_rsa_key()
        elif isinstance(obj.key, models.ECCKeyDetails):
            translator = GDKM_create_ecc_key()
        elif isinstance(obj.key, models.AuthReceipts):
            translator = GDKM_combine_auth_receipts_keyblock
        else:
            raise NotImplementedError
        self.parse = translator.parse
        return translator.serialize(obj.key, sessionId=sessionId, slot=...)

    def parse(self, msg):
        raise NotImplementedError


class GDKM_import_certificate(ByokTranslator):
    @staticmethod
    def serialize(key: models.Certificate, sessionId: str, tableType: str = None, slot: int = None):
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'import-certificate'
        msg['SI'] = sessionId

        msg['BD'] = 'FIRST' if slot is None else slot

        # Certificate type:
        # 3 - X.509 (default)
        msg['RY'] = 3

        msg['RV'] = key.certificate.hex()
        msg['LB'] = key.label
        msg['SF'] = fw_multi_sec_usage_from_name(key.securityUsage)
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage):
        key_data = models.KeySlotLoadResponseChecksum(
            kcv=msg['AE'],
        )
        return models.KeySlotLoadResponse(
            key=key_data,
            slot=int(msg['BD']),
        )


class GDKM_create_symmetric_key(ByokTranslator):
    @staticmethod
    def serialize(key: models.SymmetricKeyDetails, sessionId: str, slot: int = None) -> 'ExcryptMessage':
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'create-symmetric-keyslot' if slot is not ... else 'create-symmetric-keyblock'
        msg['SI'] = sessionId

        msg['RC'] = 'FIRST' if slot is None else slot
        msg['LB'] = key.label
        msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[key.majorKey]

        msg['AS'] = hex(key.modifier)[2:]
        msg['CT'] = GPKIKeyType.names_to_values[key.type]
        msg['CZ'] = fw_sym_key_usage_from_name(key.usage)
        msg['TF'] = fw_multi_sec_usage_from_name(key.securityUsage)
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage):
        if 'RC' in msg:
            key_data = models.KeySlotLoadResponseSymmetric(
                kcv=msg['AE'],
            )
            return models.KeySlotLoadResponse(
                key=key_data,
                slot=int(msg['RC']),
            )

        key_data = models.GenerateKeyResponseSymmetric(
            kcv=msg['AE'],
            keyBlock=msg['BG'],
        )
        return models.GenerateKeyBlockResponse(key=key_data)


class GDKM_create_rsa_key(ByokTranslator):
    def serialize(self, key: models.RSAKeyDetails, sessionId: str, slot: int = None) -> ExcryptMessage:
        self.to_slot = slot is not ...
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'create-rsa-keyslot' if self.to_slot else 'create-rsa-keyblock'
        msg['SI'] = sessionId

        msg['RA'] = f'{key.exponent:x}'
        msg['RB'] = key.modulus
        msg['RC'] = 'FIRST' if slot is None else slot
        msg['LB'] = key.label
        msg['BJ'] = MAJOR_KEY_CONSTS_REVERSED[key.majorKey]

        msg['CY'] = fw_multi_key_usage_from_name(key.usage)
        msg['TF'] = fw_multi_sec_usage_from_name(key.securityUsage)
        return msg

    def parse(self, msg: ExcryptMessage):
        if self.to_slot:
            key_data = models.KeySlotLoadResponseAsymmetric(
                kcv=msg['AE'],
                clearPublicKeyBlock=hex_der_to_pem(msg['RD'], 'PUBLIC KEY'),
                publicKeyBlock=msg['SD'],
            )
            return models.KeySlotLoadResponse(
                key=key_data,
                slot=int(msg['RC']),
            )
        key_data = models.GenerateKeyResponseAsymmetric(
            privateKeyBlock=msg['RC'],
            kcv=msg['AE'],
            clearPublicKeyBlock=hex_der_to_pem(msg['RD'], 'PUBLIC KEY'),
            publicKeyBlock=msg['SD'],
        )
        return models.GenerateKeyBlockResponse(key=key_data)


class GDKM_create_ecc_key(ByokTranslator):
    def serialize(self, key: models.ECCKeyDetails, sessionId: str, slot: int = None) -> 'ExcryptMessage':
        self.to_slot = slot is not ...
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'create-ecc-keyslot' if slot is not ... else 'create-ecc-keyblock'
        msg['SI'] = sessionId

        msg['RA'] = ECC_CURVE_OIDS[key.curve]
        msg['RC'] = 'FIRST' if slot is None else slot
        msg['LB'] = key.label
        msg['BJ'] = MAJOR_KEY_CONSTS_REVERSED[key.majorKey]

        msg['CY'] = fw_multi_key_usage_from_name(key.usage)
        msg['TF'] = fw_multi_sec_usage_from_name(key.securityUsage)
        return msg

    def parse(self, msg: ExcryptMessage):
        if self.to_slot:
            key_data = models.KeySlotLoadResponseAsymmetric(
                kcv=msg['AE'],
                clearPublicKeyBlock=hex_der_to_pem(msg['RD'], 'PUBLIC KEY'),
                publicKeyBlock=msg['SD'],
            )
            return models.KeySlotLoadResponse(
                key=key_data,
                slot=int(msg['RC']),
            )
        key_data = models.GenerateKeyResponseAsymmetric(
            privateKeyBlock=msg['RC'],
            kcv=msg['AE'],
            clearPublicKeyBlock=hex_der_to_pem(msg['RD'], 'PUBLIC KEY'),
            publicKeyBlock=msg['SD'],
        )
        return models.GenerateKeyBlockResponse(key=key_data)


class GDKM_import_symmetric_keyblock(ByokTranslator):
    @staticmethod
    def serialize(key: models.KeyBlockLoad, sessionId: str, slot: int = None) -> 'ExcryptMessage':
        assert key.keyBlock

        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'import-symmetric-keyblock'
        msg['SI'] = sessionId

        msg['BD'] = 'FIRST' if slot is None else slot
        msg['BG'] = key.keyBlock
        msg['LB'] = key.label
        msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[key.majorKey]
        msg['AS'] = hex(key.modifier)[2:]
        msg['CZ'] = fw_sym_key_usage_from_name(key.usage) if key.usage else None
        msg['SF'] = fw_multi_sec_usage_from_name(key.securityUsage) if key.securityUsage else None
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage):
        key_data = models.KeySlotLoadResponseSymmetric(
            kcv=msg['AE'],
        )
        return models.KeySlotLoadResponse(
            key=key_data,
            slot=int(msg['BD']),
        )


class GDKM_import_asymmetric_keyblock(ByokTranslator):

    @staticmethod
    def serialize(key: models.KeyBlockLoad, sessionId: str, slot: int = None) -> 'list[Union[ExcryptMessage, NoneType]]':
        major_key = MAJOR_KEY_CONSTS_REVERSED[key.majorKey]
        usage = fw_asym_key_usage_from_name(key.usage) if key.usage else None
        sec_usage = fw_multi_sec_usage_from_name(key.securityUsage) if key.securityUsage else None

        # if they gave a slot to load to, treat that as the private key slot
        # unless there's no private key, in which case treat that as the public key slot
        tpk_slot = key.tpkSlot
        if not key.privateKeyBlock and tpk_slot is None:
            tpk_slot = slot
        if tpk_slot is None:
            tpk_slot = 'FIRST'

        msgs = [None, None, None, None]
        if key.publicKeyBlock:
            msgs[0] = ExcryptMessage()
            msg = msgs[0]
            msg['AO'] = 'GDKM'
            msg['OP'] = 'import-public-keyblock'
            msg['SI'] = sessionId
            msg['SD'] = key.publicKeyBlock
            msg['RD'] = tpk_slot
            msg['LB'] = key.label + '_public' if key.label and key.privateKeyBlock else key.label
            msg['FS'] = major_key
            msg['CZ'] = usage
            msg['SF'] = sec_usage

        if key.privateKeyBlock:
            msgs[1] = ExcryptMessage()
            msg = msgs[1]
            msg['AO'] = 'GDKM'
            msg['OP'] = 'import-private-keyblock'
            msg['SI'] = sessionId
            msg['RC'] = key.privateKeyBlock
            msg['RD'] = 'FIRST' if slot is None else slot
            msg['LB'] = key.label
            msg['FS'] = major_key
            msg['CZ'] = usage
            msg['SF'] = sec_usage

        if key.privateKeyBlock:
            # get clear public key
            msgs[2] = ExcryptMessage(
                f'[AOGDKM;OPcreate-public-keyblock-from-private;AK1;SI{sessionId};FS{major_key};RC{key.privateKeyBlock};]'
            )
            if not key.publicKeyBlock:
                msgs[3] = msgs[2].copy()
                msgs[3]['AK'] = 2  # get trusted public key

        return msgs

    @staticmethod
    def parse(msgs: 'list[Optional[ExcryptMessage]]'):
        public, private, clear, tpk = msgs

        key_data = models.KeySlotLoadResponseAsymmetric(
            kcv=private and private['AE'],
            tpkKcv=public and public['AE'],
            publicKeyBlock=tpk and tpk['RD'],
            clearPublicKeyBlock=clear and hex_der_to_pem(clear['RD'], 'PUBLIC KEY'),
        )
        return models.KeySlotLoadResponse(
            key=key_data,
            slot=private and int(private['RD']),
            tpkSlot=public and int(public['RD']),
        )


class GDKM_import_diebold(ByokTranslator):
    @staticmethod
    def serialize(key: models.DieboldTable, sessionId: str, slot: int = None) -> 'ExcryptMessage':
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'import-diebold'
        msg['SI'] = sessionId

        msg['BR'] = slot if slot is not None else 'FIRST'
        msg['BO'] = key.table.hex().upper()
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage):
        return models.KeySlotLoadResponse(
            key=models.KeySlotLoadResponseChecksum(
                kcv=msg['AE'],
            ),
            slot=int(msg['BR']),
        )


class GDKM_convert_pkcs8_to_keyblock(ByokTranslator):
    @staticmethod
    def serialize(key: models.Pkcs8Load, sessionId: str, **kwargs) -> 'ExcryptMessage':
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'convert-pkcs8-to-keyblock'
        msg['SI'] = sessionId

        msg['SD'] = key.pkcs8.hex()
        msg['DB'] = key.password.hex()
        msg['FS'] = MAJOR_KEY_CONSTS_REVERSED.get(key.majorKey)
        msg['CZ'] = fw_asym_key_usage_from_name(key.usage)
        msg['SF'] = fw_multi_sec_usage_from_name(key.securityUsage)

        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.KeyBlock:
        return models.KeyBlock(
            keyBlock=msg['RC'],
        )


class GDKM_export_csr(ByokTranslator):

    def serialize(self,
                  obj: Union[models.GenerateCsrIntent, models.GenerateCsrFromKeyblockIntent],
                  sessionId: str,
                  slot: Optional[int] = None) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'export-csr'
        msg['SI'] = sessionId
        msg['KZ'] = obj.password
        if obj.pkiOptions.san:
            san_hex = obj.pkiOptions.san.encode().hex().upper()
            msg['XW'] = f'{{2.5.29.17,{san_hex},1}}'
        if obj.pkiOptions.subject:
            self.serialize_subject(obj.pkiOptions.subject, msg)
        if obj.pkiOptions.keyUsage:
            msg['KU'] = ','.join(obj.pkiOptions.keyUsage)

        if isinstance(obj, models.GenerateCsrFromKeyblockIntent):
            msg['RC'] = obj.privateKeyBlock
            msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[obj.majorKey]
        else:
            msg['RC'] = slot

        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.Csr:
        csr = hex_der_to_pem(msg['RU'], 'CERTIFICATE REQUEST')
        return models.Csr(csr=csr)

    @singledispatchmethod
    def serialize_subject(self, _, __):
        raise NotImplementedError

    @serialize_subject.register(models.DNMap)
    def serialize_subject_map(self, subject: models.DNMap, msg: ExcryptMessage):
        msg['RT'] = subject.commonName
        msg['RO'] = subject.country
        msg['RP'] = subject.stateOrProvinceName
        msg['RQ'] = subject.locality
        msg['RR'] = subject.organization
        msg['RS'] = subject.organizationalUnit
        msg['SC'] = subject.email

    @serialize_subject.register(tuple)
    def serialize_subject_string(self, subject: List[dict], msg: ExcryptMessage):
        subject = [models.RDN.schema.load(rdn_dict) for rdn_dict in subject]
        self.serialize_subject(subject, msg)

    @serialize_subject.register(list)
    def serialize_subject_list(self, subject: List[models.RDN], msg: ExcryptMessage):
        sn = '},{'.join(
            f'{rdn.oid},{rdn.asn1Type},{rdn.value.hex()}'
            for rdn in subject
        )
        sn = '{' + sn + '}'
        msg['SN'] = sn


class GDKM_export_key_slot(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, gp_mode: bool = None, tableType: str = 'symmetric', slot: int = None) -> 'list[ExcryptMessage]':
        gpgc_ct, gpks_be = {
            'diebold': ('7', '0'),
            'symmetric': ('1', '0'),
            'asymmetric': ('8', '1'),
        }.get(tableType, ('1', '0'))

        return [
            ExcryptMessage({
                'AO': 'GDKM',
                'OP': 'export-keyblock',
                'SI': sessionId,
                'CT': gpgc_ct,
                'BD': str(slot),
            }),
            ExcryptMessage({
                'AO': 'GDKM',
                'OP': 'read-keyslot',
                'SI': sessionId,
                'BE': gpks_be,
                'BD': str(slot),
            })
        ]

    @staticmethod
    def parse(msgs: 'list[ExcryptMessage]') -> models.KeySlotRetrieveResponse:
        gpgc = msgs[0]
        gpks = msgs[1]
        key = None

        typ = KEY_TYPE_CONSTS.get(gpks.get('CT', None), 'Empty')
        key_is_public = '(Public)' in typ
        if 'RSA' in typ:
            key = models.RSAKey(
                modulus=int(gpks['RB']),
                majorKey=MAJOR_KEY_CONSTS[gpks['FS']],
                kcv=gpks['AE'],
                label=gpks.get('LB'),
                usage=fw_multi_key_usage_to_name(gpks['CY']),
                securityUsage=fw_multi_sec_usage_to_name(gpks['SF']),
                publicKeyBlock=gpgc.get('BG') if key_is_public else None,
                privateKeyBlock=gpgc.get('BG') if not key_is_public else None,
            )
        elif 'ECC' in typ:
            key = models.ECCKey(
                curve=ECC_CURVE_NAMES.get(gpks.get('CU', ''), None),
                majorKey=MAJOR_KEY_CONSTS[gpks['FS']],
                kcv=gpks['AE'],
                label=gpks.get('LB'),
                usage=fw_multi_key_usage_to_name(gpks.get('CY', '')),
                securityUsage=fw_multi_sec_usage_to_name(gpks.get('SF', '')),
                publicKeyBlock=gpgc.get('BG') if key_is_public else None,
                privateKeyBlock=gpgc.get('BG') if not key_is_public else None,
            )
        elif typ == 'Diebold':
            key = models.DieboldTable(
                kcv=gpks['AE'],
            )
        elif typ == 'Certificate':
            cert_type = {  # FXPKICert::ePKICertType
                '1': 'PKCS7',
                '2': 'CERTIFICATE REQUEST',
                '3': 'CERTIFICATE',
                '4': 'X509 CRL',
            }.get(gpks.get('RY'))
            cert_data = gpks.get('RV')
            key = models.Certificate(
                certificate=hex_der_to_pem(cert_data, label=cert_type),
                label=gpks.get('LB'),
                securityUsage=fw_multi_sec_usage_to_name(gpks.get('SF', '')),
                kcv=gpks.get('AE'),
            )
        elif typ != 'Empty':  # symmetric
            key = models.SymmetricKeyBlockDetails(
                type=typ,
                majorKey=MAJOR_KEY_CONSTS[gpks['FS']],
                kcv=gpks['AE'],
                label=gpks.get('LB'),
                modifier=int(gpks.get('AS', '0')),  # GPKS returns modifier in base 10 lol
                securityUsage=fw_multi_sec_usage_to_name(gpks.get('SF', '')),
                usage=fw_multi_key_usage_to_name(gpks.get('CY', '')),
                keyBlock=gpgc.get('BG', None),
            )
        return models.KeySlotRetrieveResponse(response=key)


class GDKM_read_keyslot(ByokTranslator):
    def serialize(self, sessionId: str, tableType: str = 'symmetric', slot: int = None) -> ExcryptMessage:
        self.args = (sessionId, tableType, slot)
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'read-keyslot',
            'SI': sessionId,
            'BE': tableType == 'asymmetric',
            'BD': str(slot),
        })

    def parse(self, gpks: ExcryptMessage) -> models.KeySlotRetrieveResponse:
        key = None

        typ = KEY_TYPE_CONSTS.get(gpks.get('CT', None), 'Empty')
        key_is_public = '(Public)' in typ
        if 'RSA' in typ:
            key = models.RSAKey(
                modulus=int(gpks['RB']),
                majorKey=MAJOR_KEY_CONSTS[gpks['FS']],
                kcv=gpks['AE'],
                label=gpks.get('LB'),
                usage=fw_multi_key_usage_to_name(gpks['CY']),
                securityUsage=fw_multi_sec_usage_to_name(gpks['SF']),
                publicKeyBlock=None,
                privateKeyBlock=None,
            )
        elif 'ECC' in typ:
            key = models.ECCKey(
                curve=ECC_CURVE_NAMES.get(gpks.get('CU', ''), None),
                majorKey=MAJOR_KEY_CONSTS[gpks['FS']],
                kcv=gpks['AE'],
                label=gpks.get('LB'),
                usage=fw_multi_key_usage_to_name(gpks.get('CY', '')),
                securityUsage=fw_multi_sec_usage_to_name(gpks.get('SF', '')),
                publicKeyBlock=None,
                privateKeyBlock=None,
            )
        elif typ == 'Diebold':
            key = models.DieboldTable(
                kcv=gpks['AE'],
            )
        elif typ == 'Certificate':
            cert_type = {  # FXPKICert::ePKICertType
                '1': 'PKCS7',
                '2': 'CERTIFICATE REQUEST',
                '3': 'CERTIFICATE',
                '4': 'X509 CRL',
            }.get(gpks.get('RY'))
            cert_data = gpks.get('RV')
            key = models.Certificate(
                certificate=hex_der_to_pem(cert_data, label=cert_type),
                label=gpks.get('LB'),
                securityUsage=fw_multi_sec_usage_to_name(gpks.get('SF', '')),
                kcv=gpks.get('AE'),
            )
        elif typ != 'Empty':  # symmetric
            key = models.SymmetricKeyBlockDetails(
                type=typ,
                majorKey=MAJOR_KEY_CONSTS[gpks['FS']],
                kcv=gpks['AE'],
                label=gpks.get('LB'),
                modifier=int(gpks.get('AS', '0')),  # GPKS returns modifier in base 10 lol
                securityUsage=fw_multi_sec_usage_to_name(gpks.get('SF', '')),
                usage=fw_multi_key_usage_to_name(gpks.get('CY', '')),
                keyBlock=None,
            )
        response = models.KeySlotRetrieveResponse(response=key)
        response._args = (*self.args, key_is_public)  # pass to GDKM_export_keyblock_from_slot
        return response


class GDKM_export_keyblock_from_slot(ByokTranslator):
    def serialize(self, response: models.KeySlotRetrieveResponse) -> Optional[ExcryptMessage]:
        self.rsp = response
        sessionId, tableType, slot, _ = self.rsp._args

        if tableType == 'symmetric':
            gpgc_ct = 1
        elif tableType == 'asymmetric':
            gpgc_ct = 8
        else:
            return None

        assert isinstance(self.rsp.response, (models.SymmetricKeyBlockDetails, models.BaseAsymmetricKey))
        major_key = MAJOR_KEY_CONSTS_REVERSED[self.rsp.response.majorKey]

        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'export-keyblock',
            'SI': sessionId,
            'CT': gpgc_ct,
            'BD': str(slot),
            'FS': major_key,
        })

    def parse(self, gpgc: Optional[ExcryptMessage]) -> models.KeySlotRetrieveResponse:
        # diebold/certificate/empty, or not exportable:
        if not gpgc:
            return self.rsp

        *_, key_is_public = self.rsp._args
        key = self.rsp.response
        key_block = gpgc.get('BG')

        if key_is_public and isinstance(key, (models.RSAKey, models.ECCKey)):
            key.publicKeyBlock = key_block
        if not key_is_public and isinstance(key, (models.RSAKey, models.ECCKey)):
            key.privateKeyBlock = key_block
        elif isinstance(key, models.SymmetricKeyBlockDetails):
            key.keyBlock = key_block

        return self.rsp


class GDKM_update_key_slot(ByokTranslator):
    @staticmethod
    def serialize(obj: models.BaseKey, sessionId: str, tableType: str = 'symmetric', slot: int = None) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'update-keyslot'
        msg['SI'] = sessionId
        msg['BE'] = 1 if tableType == 'asymmetric' else 0  # 0 for symmetric or diebold
        msg['BD'] = slot

        msg['CY'] = fw_multi_key_usage_from_name(obj.usage) or '0'
        msg['SF'] = fw_multi_sec_usage_from_name(obj.securityUsage) or 0
        msg['LB'] = obj.label

        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> None:
        pass


class GDKM_delete_key_slot(ByokTranslator):
    @staticmethod
    def serialize(sessionId: str, tableType: str = None, slot: int = None) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'delete-keyslot'
        msg['SI'] = sessionId
        msg['CT'] = models.KEY_TABLE_TYPES.get(tableType, None)  # ignore type for GP mode
        msg['BD'] = slot
        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> None:
        if msg.get('AN') == 'Y':
            msg.pop('BB')  # it was successful, discard 'Y' / 'N' for whether key was deleted


class GDKM_key_block_verify(ByokTranslator):
    @staticmethod
    def serialize(obj: models.KeyBlockVerifyIntent, sessionId: str) -> List[ExcryptMessage]:
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'verify-key'
        msg['SI'] = sessionId
        msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[obj.key.majorKey]
        try:
            msg['BG'] = obj.key.keyBlock
            msg['AS'] = hex(obj.key.modifier)[2:]
        except AttributeError:
            pass
        try:
            msg['SD'] = obj.key.publicKeyBlock
        except AttributeError:
            pass
        try:
            msg['RC'] = obj.key.privateKeyBlock
        except AttributeError:
            pass

        msgs = [msg.copy(), msg]  # [GPKS, GPKB]
        msg['OP'] = 'convert-keyblock-to-tr31'

        return msgs

    @staticmethod
    def parse(msgs: List[ExcryptMessage]) -> models.KeyBlockVerifyResult:
        gpks, gpkb = msgs
        key = GDKM_export_key_slot.parse([gpks, gpks]).response

        obj = models.KeyBlockVerifyResult(
            key=key,
            tr31=parse_tr31_to_details(gpkb['BG']),
        )
        return obj


class GDKM_generate_trusted_public_key(ByokTranslator):
    @staticmethod
    def serialize(obj: models.GenerateTrustedPublicKeyIntent, sessionId: str) -> ExcryptMessage:
        msg = ExcryptMessage()
        msg['AO'] = 'GDKM'
        msg['OP'] = 'generate-tpk'
        msg['SI'] = sessionId

        msg['RD'] = obj.clearPublicKeyBlock.hex()
        msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[obj.majorKey]
        msg['CZ'] = fw_asym_key_usage_from_name(obj.usage)
        msg['SF'] = fw_multi_sec_usage_from_name(obj.securityUsage)

        return msg

    @staticmethod
    def parse(msg: ExcryptMessage) -> models.GenerateTrustedPublicKeyResult:
        return models.GenerateTrustedPublicKeyResult(
            publicKeyBlock=msg['SD'],
            kcv=None
        )


class GDKM_translate_usage_1st(ByokTranslator):
    # intended to be called in order, 1st -> 2nd -> 3rd
    # passing the *args along from one to the next and modify the key block in place
    def serialize(self, obj: models.KeyBlockTranslateIntent, sessionId: str) -> Optional[ExcryptMessage]:
        self.args = (obj, sessionId)
        change_usage = obj.usage or obj.securityUsage
        if not change_usage:
            return None

        msg = ExcryptMessage({
            'AO': 'GDKM',
            'SI': sessionId,
            'CY': fw_multi_key_usage_from_name(obj.usage),
            'SF': fw_multi_sec_usage_from_name(obj.securityUsage),
        })
        if isinstance(obj.key, models.SymmetricKeyBlock):
            msg['OP'] = 'update-symmetric-keyblock'
            msg['BG'] = obj.key.keyBlock
            msg['AS'] = to_hex(obj.key.modifier)
            msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[obj.key.majorKey]
        elif isinstance(obj.key, models.PrivateKeyBlock):
            msg['OP'] = 'update-private-keyblock'
            msg['RC'] = obj.key.privateKeyBlock
            msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[obj.key.majorKey]
        else:  # key is wrapped, we'll just change the usage in the GPKU call
            return None

        return msg

    def parse(self, msg: ExcryptMessage = None):
        kcv = None
        if msg:
            obj, _ = self.args
            kcv = msg['AE']
            if isinstance(obj.key, models.SymmetricKeyBlock):
                obj.key.keyBlock = msg['BG']
            elif isinstance(obj.key, models.PrivateKeyBlock):
                obj.key.privateKeyBlock = msg['BG']
        return (*self.args, kcv)


class GDKM_translate_kek_2nd(ByokTranslator):
    def serialize(self, obj: models.KeyBlockTranslateIntent, sessionId: str, kcv: str) -> Optional[ExcryptMessage]:
        self.args = (obj, sessionId, kcv)

        if not obj.outputFormat:
            # nothing to wrap/unwrap, maybe we're just adding a header or changing usage, skip step
            return None

        key = obj.key
        from_kek = hasattr(key, 'kekSlot')
        to_kek = isinstance(obj.outputFormat, models.WrapKeyDetails)
        symmetric_key_block = getattr(key, 'keyBlock', None)
        private_key_block = getattr(key, 'privateKeyBlock', None)

        if private_key_block and obj.header and to_kek:
            # GKBL will handle the KEK translation for PKI
            # But for symmetric keys it expects the input and output under the KEK
            return None

        msg = ExcryptMessage(f'[AOGDKM;SI{sessionId};]')

        if not from_kek and not to_kek:  # majorKey -> majorKey
            if symmetric_key_block:
                msg['OP'] = 'translate-symmetric-keyblock'
                msg['BG'] = symmetric_key_block
                msg['AS'] = to_hex(key.modifier)
            else:
                msg['OP'] = 'translate-private-keyblock'
                msg['RC'] = private_key_block
            msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[key.majorKey]
            msg['BJ'] = MAJOR_KEY_CONSTS_REVERSED[obj.outputFormat.majorKey]
        elif not from_kek and to_kek:  # majorKey -> kek
            out_format = cast(models.WrapKeyDetails, obj.outputFormat)
            msg['OP'] = 'wrap-keyblock'
            msg['AS'] = to_hex(key.modifier) if symmetric_key_block else None
            msg['BG'] = symmetric_key_block
            msg['SD'] = private_key_block
            msg['AK'] = f'BD{out_format.kekSlot}'
            msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[key.majorKey]
            if out_format.cipher:
                msg['BJ'] = FXK_CIPHER_MODES[out_format.cipher.type]
                msg['GH'] = out_format.cipher.iv and out_format.cipher.iv.hex()
                msg['ZA'] = out_format.cipher.clearIv
                msg['CE'] = out_format.cipher.padding and PADDING_MODES[out_format.cipher.padding]

        elif from_kek and not to_kek:  # kek -> majorKey
            out_format = cast(models.UnwrapKeyDetails, obj.outputFormat)
            key = cast(models.WrapKeyDetails, key)
            msg['OP'] = 'unwrap-keyblock'
            msg['AK'] = f'BD{key.kekSlot}'
            msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[out_format.majorKey]
            msg['CY'] = fw_multi_key_usage_from_name(obj.usage)
            msg['SF'] = fw_multi_sec_usage_from_name(obj.securityUsage)
            msg['AS'] = to_hex(out_format.modifier)
            msg['BG'] = symmetric_key_block or private_key_block
            if key.cipher:
                msg['BJ'] = FXK_CIPHER_MODES[key.cipher.type]
                msg['GH'] = key.cipher.iv and key.cipher.iv.hex()
                msg['ZA'] = key.cipher.clearIv
                msg['CE'] = PADDING_MODES.get(key.cipher.padding, None)
                msg['CT'] = GPKIKeyType.names_to_values[key.type]
        else:
            msg = None  # shouldn't happen, should've prohibited sending from-kek-to-kek

        return msg

    def parse(self, msg: ExcryptMessage = None):
        if msg:
            obj, session_id, kcv = self.args
            try:
                obj.key.keyBlock
            except AttributeError:
                obj.key.privateKeyBlock = msg['BG']
            else:
                obj.key.keyBlock = msg['BG']
            kcv = msg['AE']
            self.args = (obj, session_id, kcv)
        return self.args


class GDKM_translate_header_3rd(ByokTranslator):
    def serialize(self, obj: models.KeyBlockTranslateIntent, sessionId: str, kcv: str) -> Optional[ExcryptMessage]:
        self.args = (obj, sessionId, kcv)
        msg = ExcryptMessage()
        if obj.header:
            msg['AO'] = 'GDKM'
            msg['OP'] = 'add-keyblock-header'
            msg['SI'] = sessionId
            msg['AK'] = obj.header

            # Input key: Symmetric keyblock
            if hasattr(obj.key, 'keyBlock'):
                msg['BG'] = obj.key.keyBlock
                msg['AS'] = to_hex(getattr(obj.key, 'modifier', None))
            # Input key: Private keyblock
            else:
                msg['BG'] = obj.key.privateKeyBlock

            # Current major key: Translated to new majorkey
            if obj.outputFormat and not isinstance(obj.outputFormat, models.WrapKeyDetails):
                msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[obj.outputFormat.majorKey]
            # Current major key: Original major key
            else:
                msg['FS'] = MAJOR_KEY_CONSTS_REVERSED[obj.key.majorKey]

            # KEK to wrap with
            if isinstance(obj.outputFormat, models.WrapKeyDetails):  # output key is wrapped
                msg['AP'] = f'BD{obj.outputFormat.kekSlot}'
            elif not obj.outputFormat and hasattr(obj.key, 'kekSlot'):  # key wasn't translated, but is wrapped
                msg['AP'] = f'BD{obj.key.kekSlot}'
        elif not kcv:
            msg['AO'] = 'GDKM'
            msg['SI'] = sessionId
            msg['OP'] = 'verify-key'
            if isinstance(obj.key, models.SymmetricKeyBlock):
                msg['BG'] = obj.key.keyBlock
                msg['AS'] = to_hex(obj.key.modifier)
            elif isinstance(obj.key, models.PrivateKeyBlock):
                msg['SD'] = obj.key.privateKeyBlock
        else:
            msg = None
        return msg

    def parse(self, msg: ExcryptMessage = None) -> models.KeyBlockTranslateResult:
        obj, _, kcv = self.args
        try:
            key_block = obj.key.keyBlock
        except AttributeError:
            key_block = obj.key.privateKeyBlock

        if msg and msg.get('BB'):
            key_block = msg['BB']
        if msg and msg.get('AE'):
            kcv = msg['AE']

        return models.KeyBlockTranslateResult(
            keyBlock=key_block,
            kcv=kcv,
        )


class GDKM_create_random_components(ByokTranslator):
    def serialize(self, req: models.ComponentGenerationIntent, sessionId: str) -> ExcryptMessage:
        self.args = (req, sessionId)
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-random-components',
            'SI': sessionId,
            'FG': GPKIKeyType.names_to_values[req.type],
            'BJ': 1,
        })

    def parse(self, msg: ExcryptMessage):
        cont_id = msg['CH']
        result = models.ComponentGenerationResponse(
            kcv=msg['AM'],
            components=[
                models.ComponentDetails(
                    component=msg['BG'],
                    kcv=msg['AE'],
                )
            ],
        )
        # lines up with the continued serialize args:
        return (*self.args, cont_id, result)


class GDKM_create_random_components_continued(ByokTranslator):
    def serialize(self, req: models.ComponentGenerationIntent, session_id: str, cont_id: str,
                  result: models.ComponentGenerationResponse) -> Optional[List[ExcryptMessage]]:
        self.args = (req, session_id, cont_id, result)

        num_middle_components = req.numComponents - 2
        msgs = [ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-random-components',
            'SI': session_id,
            'FG': GPKIKeyType.names_to_values[req.type],
            'CH': cont_id,
            'BJ': 1,
        })] * num_middle_components
        return msgs or None

    def parse(self, msgs: Optional[List[ExcryptMessage]]):
        if msgs:
            middle = [models.ComponentDetails(component=msg['BG'], kcv=msg['AE']) for msg in msgs]
            result = self.args[-1]
            result.components.extend(middle)
        # lines up with the final serialize args:
        return self.args


class GDKM_create_random_components_final(ByokTranslator):
    def serialize(self, req: models.ComponentGenerationIntent, session_id: str, cont_id: str,
                  result: models.ComponentGenerationResponse) -> ExcryptMessage:
        self.result = result

        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-random-components',
            'SI': session_id,
            'FG': GPKIKeyType.names_to_values[req.type],
            'CH': cont_id,
            'BJ': 0,
        })

    def parse(self, msg: ExcryptMessage) -> models.ComponentGenerationResponse:
        self.result.components.append(
            models.ComponentDetails(component=msg['BG'], kcv=msg['AE'])
        )
        return self.result


class GDKM_convert_keyblock_to_fragment_id(ByokTranslator):
    def serialize(self, req: models.KeyBlockFragmentIntent, sessionId: str) -> ExcryptMessage:
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'export-scek-fragments' if req.encrypted else 'convert-keyblock-to-fragments',
            'SI': sessionId,
            'AH': req.key.keyBlock,
            'AS': req.key.modifier,  # note KEYF reads the modifier in decimal not hex lol
            'MK': MAJOR_KEY_CONSTS_REVERSED.get(req.key.majorKey),
            'BJ': req.m,
            'BO': req.n,
        })

    def parse(self, msg: ExcryptMessage) -> str:
        return msg['CH']


class GDKM_export_fragment_id(ByokTranslator):
    def serialize(self, req: models.KeyBlockFragmentIntent, sessionId: str, slot: int) -> ExcryptMessage:
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'export-scek-fragments' if req.encrypted else 'export-fragments',
            'SI': sessionId,
            'BD': slot,
            'BJ': req.m,
            'BO': req.n,
        })

    def parse(self, msg: ExcryptMessage) -> str:
        return msg['CH']


class GDKM_export_fragments(ByokTranslator):
    def serialize(self, req: models.KeyBlockFragmentIntent, sessionId: str, cont_id: str) -> List[ExcryptMessage]:
        return [ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'export-scek-fragments-cont' if req.encrypted else 'export-fragments-cont',
            'SI': sessionId,
            'CH': cont_id,
            'BN': fragmentNumber,
        }) for fragmentNumber in range(1, req.n + 1)]

    def parse(self, msgs: List[ExcryptMessage]) -> models.KeyFragments:
        return models.KeyFragments(
            kcv=msgs[0]['AE'],
            fragments=[
                models.KeyFragment(
                    fragment=msg['WA'],
                    kcv=msg['XA'],
                )
                for msg in msgs
            ]
        )


class GDKM_combine_auth_receipts_keyblock_id(ByokTranslator):
    @staticmethod
    def serialize(req: models.AuthReceipts, sessionId: str) -> ExcryptMessage:
        # just do the first component/fragment in order to get a continuation ID
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-keyblock-from-cskl-receipts',
            'SI': sessionId,
            'DB': req.authReceipts[0],
            'TF': 1,  # for auth receipts only need to access the main card
        })

    @staticmethod
    def parse(msg: ExcryptMessage) -> str:
        # we may have actually gotten the completed keyblock already so return early
        if msg.get('BG'):
            key = models.RecombinedKey(
                keyBlock=msg.get('BG'),
                kcv=msg.get('AE'),
            )
            raise StopIteration(models.GenerateKeyBlockResponse(key=key))
        # otherwise get the continuation ID for the rest of the auth receipts
        return msg['CH']


class GDKM_combine_auth_receipts_keyblock(ByokTranslator):
    @staticmethod
    def serialize(req: models.AuthReceipts, sessionId: str, slot = None) -> List[ExcryptMessage]:
        return [ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-keyblock-from-cskl-receipts-cont',
            'SI': sessionId,
            'CH': req._continuation_id,
            'DB': auth_receipt,
            'TF': 1,
        }) for auth_receipt in req.authReceipts[1:]]

    @staticmethod
    def parse(msgs: List[ExcryptMessage]) -> models.GenerateKeyBlockResponse:
        key_block = first(msg.get('BG') for msg in msgs)
        kcv = first(msg.get('AE') for msg in msgs)
        key = models.RecombinedKey(
            keyBlock=key_block,
            kcv=kcv,
        )
        return models.GenerateKeyBlockResponse(key=key)


class GDKM_combine_auth_receipts_keyslot_id(ByokTranslator):
    @staticmethod
    def serialize(req: models.LabeledAuthReceipts, sessionId: str, slot: int) -> ExcryptMessage:
        # just do the first component/fragment in order to get a continuation ID
        return ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-keyslot-from-cskl-receipts',
            'SI': sessionId,
            'DB': req.authReceipts[0],
            'TF': 1,
            'BG': 'FIRST' if slot is None else slot,
            'LB': req.label,
            'FS': MAJOR_KEY_CONSTS_REVERSED[req.majorKey],
        })

    @staticmethod
    def parse(msg: ExcryptMessage) -> str:
        # we may have actually gotten the completed keyblock already so return early
        if msg.get('BG'):
            key = models.RecombinedKey(kcv=msg.get('AE'))
            raise StopIteration(models.KeySlotLoadResponse(
                key=key,
                slot=msg.get('BD'),
            ))
        # otherwise get the continuation ID for the rest of the auth receipts
        return msg['CH']


class GDKM_combine_auth_receipts_keyslot(ByokTranslator):
    @staticmethod
    def serialize(req: models.LabeledAuthReceipts, sessionId: str, slot: int) -> List[ExcryptMessage]:
        return [ExcryptMessage({
            'AO': 'GDKM',
            'OP': 'create-keyslot-from-cskl-receipts-cont',
            'SI': sessionId,
            'CH': req._continuation_id,
            'DB': auth_receipt,
            'TF': 1,
            'BG': 'FIRST' if slot is None else slot,
            'LB': req.label,
            'FS': MAJOR_KEY_CONSTS_REVERSED[req.majorKey],
        }) for auth_receipt in req.authReceipts[1:]]

    @staticmethod
    def parse(msgs: List[ExcryptMessage]) -> models.KeySlotLoadResponse:
        slot = first(msg.get('BD') for msg in msgs)
        kcv = first(msg.get('AE') for msg in msgs)
        key = models.KeySlotLoadResponseChecksum(kcv=kcv)
        return models.KeySlotLoadResponse(
            key=key,
            slot=slot,
        )
