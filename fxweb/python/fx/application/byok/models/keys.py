"""
@file      byok/models/keys.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Resources and intents for key management
"""

from typing import List, Optional, Sequence, Union

from marshmallow import ValidationError, post_load, validates_schema
from marshmallow.validate import Length, OneOf, Range

from lib.utils.hapi_excrypt_map import DefaultRDNs, FixedDNOIDTypes

from byok import Model, field
from byok.models.base import (BasePaginationIntent, BasePaginationResponse,
                              NewType)
from byok.models.shared import (AsymKeyMultiUsage, Base64Str, CipherType,
                                EccCurve, Hex, KeyBlockMultiSecUsage,
                                KeyBlockStr, KeyChecksum, KeyLabel, KeyModifier, KeyMultiSecUsage,
                                KeyMultiUsage, KeySlot, KeyType, MajorKey, PaddingMode,
                                PemField, PemOrB64Der, PkiKeyUsage,
                                SubjectString, SymKeyMultiUsage,
                                SymmetricKeyType, require_at_least_one,
                                require_implication, require_not_together,
                                require_separate)

KEY_TABLE_TYPES = {
    'symmetric': 1,
    'diebold': 7,
    'asymmetric': 8,
    # 'certificate': 14,  # Disallow explicitly specifying certificate table (implies financial mode)
}
KeyTableType = NewType('Key Table Type', str, validate=OneOf(KEY_TABLE_TYPES.keys()))

DieboldTableData = Hex

class KeyTableKeyTotal(Model):
    available: int = field(description='Number of available keys of this type')
    used: int = field(description='Number of used keys of this type')


class KeyTableSummary(Model):
    total: KeyTableKeyTotal
    symmetric: KeyTableKeyTotal
    diebold: KeyTableKeyTotal
    rsa512: KeyTableKeyTotal
    rsa1024: KeyTableKeyTotal
    rsa2048: KeyTableKeyTotal
    rsa3072: KeyTableKeyTotal
    rsa4096: KeyTableKeyTotal
    ecc: KeyTableKeyTotal
    certificate: KeyTableKeyTotal
    financial: bool = field(description='Financial mode key indexing type')


class KeySlotSummary(Model):
    slot: KeySlot = field(required=True, description='Key slot number')
    kcv: KeyChecksum = field(dump_default='', description='Key checksum value')
    label: KeyLabel = field(dump_default='', description='Key label')
    modifier: KeyModifier = field(dump_default=0, description='Key modifier')
    type: KeyType = field(required=True, description='Key type')
    majorKey: MajorKey = field(dump_default='', description='Major key')
    usage: KeyMultiUsage = field(dump_default=(), description='Key usage flags')
    securityUsage: KeyMultiSecUsage = field(dump_default=(), descripton='Security usage flags')


class KeySlotListIntent(BasePaginationIntent):
    search: str = field(load_default='',
                        required=False,
                        description='Limit results to keys matching criteria')
    orderBy: str = field(load_default='slot',
                         required=False,
                         description='Sort pages of results by property',
                         validate=OneOf(KeySlotSummary.__annotations__))
    ascending: bool = field(load_default=True, required=False)
    includeEmpty: bool = field(load_default=False,
                               required=False,
                               description='Include empty key slots in response')


class KeySlotList(BasePaginationResponse):
    keys: Sequence[KeySlotSummary] = field(dump_default=())
    minSlot: Optional[KeySlot] = field(dump_default=None,
                                       description='Lowest non-empty matching slot')
    maxSlot: Optional[KeySlot] = field(dump_default=None,
                                       description='Highest non-empty matching slot')

    examples = {
        "Example": {
            "keys": [
                {
                    "kcv": "D39A",
                    "label": "EciesRequiresDeriveUsage",
                    "majorKey": "PMK",
                    "modifier": 0,
                    "securityUsage": ["Private"],
                    "slot": 0,
                    "type": "ECC",
                    "usage": ["Derive"],
                }
            ],
            "maxSlot": 299,
            "minSlot": 0,
            "nextPage": 2,
            "page": 1,
            "pageCount": 1,
            "totalItems": 1,
            "totalPages": 4
        }
    }


class BaseKey(Model):
    usage: KeyMultiUsage
    securityUsage: Optional[KeyMultiSecUsage]
    label: Optional[KeyLabel]


class SymmetricKeyDetails(BaseKey):
    usage: Optional[SymKeyMultiUsage]
    type: SymmetricKeyType = field(description='Key algorithm')
    modifier: KeyModifier = field(description='Major key modifier')
    majorKey: MajorKey = field(description='Major key to generate the key under')
    kcv: KeyChecksum = field(dump_only=True, dump_default=None)


class KeyBlock(Model):
    keyBlock: Optional[KeyBlockStr] = field(description='HSM-trusted key material')


class SymmetricKeyBlockDetails(SymmetricKeyDetails, KeyBlock):
    pass


class Tr31KeyBlockDetails(Model):
    class OptionalBlock(Model):
        id: str
        value: str

    header: str
    version: str
    # method: str ??
    usage: str
    algorithm: str
    modeOfUse: str
    keyVersion: str
    exportability: str
    optionalBlocks: List[OptionalBlock]


class BaseAsymmetricKey(BaseKey):
    usage: AsymKeyMultiUsage
    majorKey: MajorKey


class RSAKeyDetails(BaseAsymmetricKey):
    modulus: int = field(validate=Range(512, 4096))
    exponent: int = field(required=False, dump_default=None, load_default=65537)
    kcv: KeyChecksum = field(dump_only=True, dump_default=None)


class RSAKey(RSAKeyDetails):
    privateKeyBlock: Optional[KeyBlockStr] = field(load_default=None)
    publicKeyBlock: Optional[KeyBlockStr] = field(load_default=None)


class ECCKeyDetails(BaseAsymmetricKey):
    curve: EccCurve = field(description='OID of curve')
    kcv: KeyChecksum = field(dump_only=True, dump_default=None)


class ECCKey(ECCKeyDetails):
    privateKeyBlock: Optional[KeyBlockStr] = field(load_default=None)
    publicKeyBlock: Optional[KeyBlockStr] = field(load_default=None)


class DieboldTable(Model):
    kcv: KeyChecksum = field(dump_only=True, dump_default=None)
    table: DieboldTableData = field(dump_default=None, validate=Length(equal=256))


class KeyBlockLoad(Model):
    majorKey: MajorKey
    keyBlock: KeyBlockStr = field(dump_default=None)
    privateKeyBlock: KeyBlockStr = field(dump_default=None)
    publicKeyBlock: KeyBlockStr = field(dump_default=None)

    label: KeyLabel = field(dump_default=None)
    usage: KeyMultiUsage = field(dump_default=None)
    securityUsage: KeyMultiSecUsage = field(dump_default=None)
    modifier: KeyModifier = field(dump_default=None)

    tpkSlot: KeySlot = field(dump_default=None, description='Key slot to save trusted public key in')

    _validate_something_to_load = require_at_least_one('keyBlock', 'privateKeyBlock', 'publicKeyBlock')
    _validate_sym_or_asym = require_separate('keyBlock', ('privateKeyBlock', 'publicKeyBlock'))
    _validate_modifier_if_symmetric = require_implication('keyBlock', 'modifier')
    _validate_tpk_if_slot = require_implication('tpkSlot', 'publicKeyBlock')


class Pkcs8Load(Model):
    pkcs8: PemOrB64Der
    password: Base64Str
    majorKey: MajorKey
    usage: Optional[AsymKeyMultiUsage]
    securityUsage: Optional[KeyMultiSecUsage]
    label: Optional[KeyLabel]


class Certificate(Model):
    certificate: PemOrB64Der
    label: Optional[KeyLabel]
    securityUsage: Optional[KeyMultiSecUsage]
    kcv: KeyChecksum = field(dump_only=True, dump_default=None)


class AuthReceipts(Model):
    _continuation_id: str = field(hidden=True, dump_only=True, dump_default=None)
    authReceipts: List[str] = field(validate=Length(1))


class GenerateKeyBlockIntent(Model):
    key: Union[SymmetricKeyDetails, RSAKeyDetails, ECCKeyDetails, AuthReceipts]


class RecombinedKey(KeyBlock):
    kcv: KeyChecksum = field(description='Checksum value of combined key')


class LabeledAuthReceipts(AuthReceipts):
    label: Optional[KeyLabel]
    majorKey: Optional[MajorKey] = field(default='PMK')


class KeySlotLoadIntent(Model):
    key: Union[SymmetricKeyDetails, RSAKeyDetails, ECCKeyDetails, DieboldTable, KeyBlockLoad, Pkcs8Load, Certificate, LabeledAuthReceipts]


class KeySlotLoadResponseSymmetric(Model):
    kcv: KeyChecksum


class KeySlotLoadResponseAsymmetric(Model):
    kcv: Optional[KeyChecksum]
    publicKeyBlock: Optional[KeyBlockStr]
    clearPublicKeyBlock: Optional[PemField]
    tpkKcv: Optional[KeyChecksum] = field(dump_default=None, description='Key checksum value of loaded public key')


class KeySlotLoadResponseChecksum(Model):
    kcv: KeyChecksum


class KeySlotLoadResponse(Model):
    key: Union[KeySlotLoadResponseSymmetric, KeySlotLoadResponseAsymmetric, KeySlotLoadResponseChecksum, RecombinedKey]
    slot: Optional[KeySlot] = field(description='Key slot of loaded key')
    tpkSlot: Optional[KeySlot] = field(dump_default=None, description='Key slot of loaded public key')


class GenerateKeyResponseSymmetric(KeyBlock):
    kcv: KeyChecksum


class GenerateKeyResponseAsymmetric(Model):
    privateKeyBlock: KeyBlockStr
    kcv: KeyChecksum
    publicKeyBlock: Optional[KeyBlockStr]
    clearPublicKeyBlock: Optional[PemField]
    tpkKcv: Optional[KeyChecksum] = field(dump_default=None, description='Key checksum value of loaded public key')


class GenerateKeyBlockResponse(Model):
    key: Union[GenerateKeyResponseSymmetric, GenerateKeyResponseAsymmetric, RecombinedKey]


class KeySlotRetrieveResponse(Model):
    response: Union[SymmetricKeyBlockDetails, RSAKey, ECCKey, DieboldTable, Certificate]


class PrivateKeyBlock(Model):
    privateKeyBlock: KeyBlockStr
    majorKey: MajorKey


class PublicKeyBlock(Model):
    publicKeyBlock: KeyBlockStr
    majorKey: MajorKey


class SymmetricKeyBlock(Model):
    keyBlock: KeyBlockStr
    majorKey: MajorKey
    modifier: KeyModifier


class KeyBlockVerifyIntent(Model):
    key: Union[PrivateKeyBlock, PublicKeyBlock, SymmetricKeyBlock]


class KeyBlockVerifyResult(Model):
    key: Union[SymmetricKeyBlockDetails, RSAKey, ECCKey]
    tr31: Tr31KeyBlockDetails

    # shares same translator, so the types here need to be a subset
    _types_here = __annotations__['key'].__args__
    _types_there = KeySlotRetrieveResponse.__annotations__['response'].__args__
    assert all(map(_types_there.__contains__, _types_here))
    del _types_here
    del _types_there


class GenerateTrustedPublicKeyIntent(Model):
    clearPublicKeyBlock: PemOrB64Der
    majorKey: MajorKey
    usage: Optional[AsymKeyMultiUsage]
    securityUsage: Optional[KeyMultiSecUsage]


class GenerateTrustedPublicKeyResult(Model):
    publicKeyBlock: KeyBlockStr
    kcv: KeyChecksum


class CipherDetails(Model):
    type: CipherType
    iv: Optional[Hex]
    clearIv: Optional[bool]
    padding: Optional[PaddingMode]

    _validate_clear_has_iv = require_implication('clearIv', 'iv')

    @validates_schema
    def _validate_no_iv_if_ecb(_, data, **kwargs):
        if data.get('type') == 'ECB' and data.get('iv'):
            raise ValidationError('Field cannot be combined with type="ECB"', 'iv')


class WrapKeyDetails(Model):
    type: Optional[KeyType]
    cipher: Optional[CipherDetails]
    kekSlot: KeySlot = field(description='Key slot of the wrapping key')


class WrappedSymmetricKeyBlock(WrapKeyDetails):
    keyBlock: KeyBlockStr = field(description='Wrapped symmetric key material')


class WrappedPrivateKeyBlock(WrapKeyDetails):
    privateKeyBlock: KeyBlockStr = field(description='Wrapped private key material')


class UnwrapKeyDetails(Model):
    majorKey: MajorKey
    modifier: Optional[KeyModifier]


class KeyBlockTranslateIntent(Model):
    key: Union[SymmetricKeyBlock, PrivateKeyBlock, WrappedSymmetricKeyBlock, WrappedPrivateKeyBlock]
    outputFormat: Optional[Union[UnwrapKeyDetails, WrapKeyDetails]]
    header: Optional[str]
    usage: Optional[KeyMultiUsage]
    securityUsage: Optional[KeyBlockMultiSecUsage]

    _something_to_do = require_at_least_one('outputFormat', 'header', 'usage', 'securityUsage')
    _no_kek_to_kek = require_not_together('key.kekSlot', 'outputFormat.kekSlot')
    _no_changing_modifier = require_not_together('key.modifier', 'outputFormat.modifier')
    _raw_decrypt_requires_algorithm = require_implication('key.cipher.type', 'key.type')


class KeyBlockTranslateResult(Model):
    keyBlock: KeyBlockStr
    kcv: KeyChecksum


class DNMap(Model):
    commonName: Optional[str]
    country: Optional[str]
    stateOrProvinceName: Optional[str]
    locality: Optional[str]
    organization: Optional[str]
    organizationalUnit: Optional[str]
    email: Optional[str]


class RDN(Model):
    oid: str
    value: Hex
    asn1Type: Optional[int]

    @post_load
    def check_and_coerce(self, request, **kwargs):
        # Accept OIDs (2.5.4.3) or supported aliases (CN or commonName), but load as OID
        oid: str = request["oid"]
        if all(map(str.isdigit, oid.split("."))):
            pass
        elif oid in DefaultRDNs:
            oid = DefaultRDNs[oid]
        else:
            choices = ", ".join(sorted(DefaultRDNs.keys()))
            raise ValidationError("Must be a valid OID or one of: {}".format(choices), "oid")

        # Use default of UTF-8 unless this OID has a fixed ASN.1 type
        asn1Type = int(FixedDNOIDTypes.get(oid, 12))

        # Success, now save the translated types
        request["oid"] = oid
        request["asn1Type"] = asn1Type
        return request


class PkiOptions(Model):
    subject: Optional[Union[DNMap, List[RDN], SubjectString]]
    san: Optional[str]
    keyUsage: Optional[PkiKeyUsage]

    _some_name_required = require_at_least_one('subject', 'san')


class GenerateCsrIntent(Model):
    password: Optional[Base64Str]
    pkiOptions: PkiOptions


class GenerateCsrFromKeyblockIntent(GenerateCsrIntent):
    privateKeyBlock: KeyBlockStr
    majorKey: MajorKey


class Csr(Model):
    csr: PemField


class ComponentGenerationIntent(Model):
    type: SymmetricKeyType = field(description='Algorithm for generated key')
    numComponents: int = field(description='Number of components to generate', validate=Range(2, 12))


class ComponentDetails(Model):
    component: KeyBlockStr
    kcv: KeyChecksum


class ComponentGenerationResponse(Model):
    kcv: KeyChecksum
    components: List[ComponentDetails]


class KeyFragmentIntent(Model):
    m: int = field(description='Minimum fragments to reassemble key', validate=Range(2, 12))
    n: int = field(description='Total fragments to generate', validate=Range(2, 24))
    encrypted: bool = field(description='Encrypt fragments under remote SCEK', dump_default=False)


class KeyBlockFragmentIntent(KeyFragmentIntent):
    # inherit m, n, encrypted
    key: SymmetricKeyBlock = field(description='Key to fragment')


class KeyFragment(Model):
    fragment: str
    kcv: KeyChecksum = field(dump_only=True, dump_default=None)


class KeyFragments(Model):
    fragments: List[KeyFragment]
    kcv: KeyChecksum
