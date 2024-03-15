"""
@file      byok/views/keys.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Views for key management
"""

from typing import Optional, cast

from flask import request

import byok.models.keys as models
import byok.translators.keys as translators
from byok import BaseResponse, Blueprint, ByokView, abort
from byok.translators.crypto import RAND
from byok.utils.diebold import gen_diebold
from byok.utils.key_table import invalidates_keytable_cache
from byok.views.base import translate_with

bp_keytable = Blueprint(name='Key Table Management')
bp_keyblock = Blueprint(name='Key Block Operations')


@bp_keytable.route('/clusters/sessions/<sessionId>/keytable/info')
class KeySlotInfoView(ByokView):

    errors = {
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
    }

    def handle_errors(self, msg):
        # Handle AOCONF;FS13; not returning any status code
        if msg.get('BO'):
            return
        return super().handle_errors(msg)

    @bp_keytable.success(models.KeyTableSummary)
    @translate_with(translators.GDKM_read_keytable_counts)
    def get(self, sessionId: str):
        """
        Retrieve Key Table Summary
        """


@bp_keytable.route('/clusters/sessions/<sessionId>/keytable')
@bp_keytable.route(f'/clusters/sessions/<sessionId>/keytable/<any({",".join(models.KEY_TABLE_TYPES)}):tableType>')
class KeySlotsView(ByokView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate_route()
    def _validate_route(self):
        assert request.view_args  # how did we get here?
        gp_mode = self.server_interface.session_is_gp_mode(request.view_args['sessionId'])
        if gp_mode is None:
            return

        request_gp_table = 'tableType' not in request.view_args
        if request_gp_table ^ gp_mode:
            abort(404, 'Key table mode mismatch (Financial/General Purpose)')

    errors = {
        'VALUE OUT OF RANGE': 400,
        'FIELD OUT OF RANGE': 400,  # why is this even different than value out of range?
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
        'LABEL NOT UNIQUE': 409,
        'KEY NOT MODIFIABLE': 409,
        'INVALID CONFIGURATION': 422,
        'INVALID (PUBLIC|PRIVATE) KEY DATA': 422,
        'KEY GENERATION IN PROGRESS': 503,
    }

    @invalidates_keytable_cache
    @bp_keytable.success(models.KeySlotLoadResponse)
    @bp_keytable.json(models.KeySlotLoadIntent)
    @translate_with(translators.GDKM_load_key, preprocess=True, postprocess=True)
    def post(self, obj: Optional[models.KeySlotLoadIntent] = None,
             sessionId: str = '', tableType: Optional[str] = None,
             slot: Optional[int] = None, response = None):
        """
        Load key
        """
        if response:
            return self._fix_asyl_keyslot_offset(response)

        assert obj  # shouldn't happen

        if isinstance(obj.key, models.Pkcs8Load):
            # no command to load a pkcs8, so convert to a keyblock and load that
            sec_usage = obj.key.securityUsage
            obj.key.securityUsage = None  # leave for the GPKA call, as we're making a key block first
            to_keyblock = translate_with(translators.GDKM_convert_pkcs8_to_keyblock)(lambda: None)
            decrypted_key = to_keyblock(self, obj.key, sessionId=sessionId, tableType=tableType, slot=slot)
            obj.key = models.KeyBlockLoad(
                privateKeyBlock=decrypted_key.keyBlock,
                securityUsage=sec_usage,
                label=obj.key.label,
                majorKey=obj.key.majorKey,
            )
        elif isinstance(obj.key, models.AuthReceipts):
            # call KCCR with 1st auth receipt to get a continuation id
            get_cont_id = translate_with(translators.GDKM_combine_auth_receipts_keyslot_id)(lambda: None)
            try:
                cont_id = cast(str, get_cont_id(self, obj.key, sessionId=sessionId, slot=slot))
            except StopIteration as e:  # may have gotten a key block immediately so just return early
                return e.value
            obj.key._continuation_id = cont_id

        self.obj, self.session_id = obj, sessionId
        return obj, sessionId, tableType, slot

    def _fix_asyl_keyslot_offset(self, response: models.KeySlotLoadResponse):
        # workaround for a bug where ASYL may not return the loaded slot # with the right offset
        # only affects financial mode:
        if self.server_interface.session_is_gp_mode(self.session_id):
            return response

        FXK_ASYMMETRIC_OFFSET_GSP = 25024 + 125  # financ_max_sym_keys + financ_max_diebold_tables
        FXK_ASYMMETRIC_OFFSET_EXP = 4000 + 125

        if not response.slot:
            pass
        elif response.slot >= FXK_ASYMMETRIC_OFFSET_GSP:
            response.slot -= FXK_ASYMMETRIC_OFFSET_GSP
        elif response.slot >= FXK_ASYMMETRIC_OFFSET_EXP:
            response.slot -= FXK_ASYMMETRIC_OFFSET_EXP
        # else: the ASYL bug was fixed

        if not response.tpkSlot:
            pass
        elif response.tpkSlot >= FXK_ASYMMETRIC_OFFSET_GSP:
            response.tpkSlot -= FXK_ASYMMETRIC_OFFSET_GSP
        elif response.tpkSlot >= FXK_ASYMMETRIC_OFFSET_EXP:
            response.tpkSlot -= FXK_ASYMMETRIC_OFFSET_EXP

        return response

    @bp_keytable.params(models.KeySlotListIntent)
    @bp_keytable.success(models.KeySlotList)
    def get(self, query: models.KeySlotListIntent, sessionId: str, tableType: str = 'symmetric'):
        """
        List keys
        """
        key_type = models.KEY_TABLE_TYPES.get(tableType, 1)
        search = query.search or ''

        full_results = self.server_interface.query_keyslots(session_id=sessionId,
                                                            key_type=key_type,
                                                            search=search,
                                                            order_by=query.orderBy,
                                                            ascending=query.ascending,
                                                            empty=query.includeEmpty)

        offset = (query.page - 1) * query.pageCount
        page_results = full_results[offset:offset + query.pageCount]
        response = models.KeySlotList(keys=page_results)

        response.minSlot = full_results[0].slot if full_results else None
        response.maxSlot = full_results[-1].slot if full_results else None

        response.page = query.page
        response.pageCount = query.pageCount
        response.totalItems = len(full_results)
        response.update_pagination()

        return response


@bp_keytable.route('/clusters/sessions/<sessionId>/keytable/<int:slot>')
@bp_keytable.route(f'/clusters/sessions/<sessionId>/keytable/<any({",".join(models.KEY_TABLE_TYPES)}):tableType>/<int:slot>')
class KeySlotCrudView(ByokView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate_route()
    def _validate_route(self):
        assert request.view_args  # how did we get here?
        gp_mode = self.server_interface.session_is_gp_mode(request.view_args['sessionId'])
        if gp_mode is None:
            return

        request_gp_table = 'tableType' not in request.view_args
        if request_gp_table ^ gp_mode:
            abort(404, 'Key table mode mismatch (Financial/General Purpose)')

    errors = KeySlotsView.errors

    def handle_errors(self, msg):
        # we can still continue even if the GPGC call errors, ex if the key is a Diebold table:
        if request.method == 'GET' and msg.message in ('KEY IS SENSITIVE', 'INCORRECT KEY TYPE'):
            return
        # GPKD returns BBY on success:
        elif msg.status == 'Y':
            return
        return super().handle_errors(msg)

    post = KeySlotsView.post
    _fix_asyl_keyslot_offset = KeySlotsView._fix_asyl_keyslot_offset

    @bp_keytable.success(models.KeySlotRetrieveResponse)
    @translate_with(translators.GDKM_read_keyslot, postprocess=True)
    @translate_with(translators.GDKM_export_keyblock_from_slot)
    def get(self):
        """
        Export key from key slot
        """

    @invalidates_keytable_cache
    @bp_keytable.json(models.BaseKey)
    @bp_keytable.success(BaseResponse)
    @translate_with(translators.GDKM_update_key_slot)
    def patch(self):
        """
        Modify key slot properties
        """

    @invalidates_keytable_cache
    @bp_keytable.success(BaseResponse)
    @translate_with(translators.GDKM_delete_key_slot)
    def delete(self):
        """
        Erase key slot
        """


@bp_keytable.route('/clusters/sessions/<sessionId>/keytable/<int:slot>/fragment')
@bp_keytable.route(f'/clusters/sessions/<sessionId>/keytable/symmetric/<int:slot>/fragment')
class KeySlotFragmentView(ByokView):

    errors = KeySlotsView.errors

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate_route()
    def _validate_route(self):
        assert request.view_args  # how did we get here?
        gp_mode = self.server_interface.session_is_gp_mode(request.view_args['sessionId'])
        if gp_mode is None:
            return

        request_gp_table = '/symmetric/' not in request.path
        if request_gp_table ^ gp_mode:
            abort(404, 'Key table mode mismatch (Financial/General Purpose)')

    @bp_keytable.json(models.KeyFragmentIntent)
    @bp_keytable.success(models.KeyFragments)
    @translate_with(translators.GDKM_export_fragments, preprocess=True)
    def post(self, req: models.KeyBlockFragmentIntent, sessionId: str, slot: int):
        """
        Fragment key slot
        """
        get_cont_id = translate_with(translators.GDKM_export_fragment_id)(lambda: None)
        cont_id = get_cont_id(self, req, sessionId=sessionId, slot=slot)
        return req, sessionId, cont_id


@bp_keytable.route('/clusters/sessions/<sessionId>/keytable/<int:slot>/generate-csr')
@bp_keytable.route(f'/clusters/sessions/<sessionId>/keytable/asymmetric/<int:slot>/generate-csr')
class KeySlotGenerateCsrView(ByokView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate_route()
    def _validate_route(self):
        assert request.view_args  # how did we get here?
        gp_mode = self.server_interface.session_is_gp_mode(request.view_args['sessionId'])
        if gp_mode is None:
            return

        request_gp_table = '/asymmetric/' not in request.path
        if request_gp_table ^ gp_mode:
            abort(404, 'Key table mode mismatch (Financial/General Purpose)')

    @bp_keytable.json(models.GenerateCsrIntent)
    @bp_keytable.success(models.Csr)
    @translate_with(translators.GDKM_export_csr)
    def post(self):
        """
        Generate PKCS10 Request from private key
        """


@bp_keyblock.route('/keyblock/diebold/random')
class RandomDieboldTableView(ByokView):
    def handle_errors(self, msg):
        if 'AK' not in msg:  # no success tag for RAND
            return super().handle_errors(msg)

    @bp_keyblock.success(models.DieboldTable)
    @translate_with(RAND, preprocess=True, postprocess=True)
    def post(self, response=None):
        """
        Generate random Diebold table
        """
        if response is None:  # preprocess
            # number of bytes to request from AORAND, need 210 minimum: ceil((log_2(255!)+3)/8)
            # so 220 would be many "age of the universe"s more than enough
            return (220,)
        else:  # postprocess
            return models.DieboldTable(table=gen_diebold(response))


@bp_keyblock.route('/clusters/sessions/<sessionId>/keyblock')
class KeyBlockView(ByokView):

    errors = KeySlotsView.errors

    @bp_keyblock.json(models.GenerateKeyBlockIntent)
    @bp_keyblock.success(models.GenerateKeyBlockResponse)
    @translate_with(translators.GDKM_generate_key_block, preprocess=True)
    def post(self, req: models.GenerateKeyBlockIntent, sessionId: str):
        """
        Create key block
        """
        # if they want to recombine auth receipts, first get a continuation ID for it
        if isinstance(req.key, models.AuthReceipts):
            get_cont_id = translate_with(translators.GDKM_combine_auth_receipts_keyblock_id)(lambda: None)
            try:
                cont_id = cast(str, get_cont_id(self, req.key, sessionId=sessionId))
            except StopIteration as e:  # may get the key on first request so just return early
                return e.value
            req.key._continuation_id = cont_id
        return req, sessionId


@bp_keyblock.route('/clusters/sessions/<sessionId>/keyblock/info')
class KeyBlockInfoView(ByokView):

    @bp_keyblock.json(models.KeyBlockVerifyIntent)
    @bp_keyblock.success(models.KeyBlockVerifyResult)
    @translate_with(translators.GDKM_key_block_verify)
    def post(self):
        """
        Verify key block
        """


@bp_keytable.route('/clusters/sessions/<sessionId>/keyblock/fragment')
class KeyBlockFragmentView(ByokView):

    errors = KeySlotsView.errors

    @bp_keytable.json(models.KeyBlockFragmentIntent)
    @bp_keytable.success(models.KeyFragments)
    @translate_with(translators.GDKM_export_fragments, preprocess=True)
    def post(self, req: models.KeyBlockFragmentIntent, sessionId: str):
        """
        Fragment key block
        """
        get_cont_id = translate_with(translators.GDKM_convert_keyblock_to_fragment_id)(lambda: None)
        cont_id = get_cont_id(self, req, sessionId=sessionId)
        return req, sessionId, cont_id


@bp_keyblock.route("/clusters/sessions/<sessionId>/pki/generate-tpk")
class GenerateTrustedPublicKeyView(ByokView):

    @bp_keyblock.json(models.GenerateTrustedPublicKeyIntent)
    @bp_keyblock.success(models.GenerateTrustedPublicKeyResult)
    @translate_with(translators.GDKM_generate_trusted_public_key, preprocess=True, postprocess=True)
    def post(self,
             data: models.GenerateTrustedPublicKeyIntent = None,
             sessionId: str = None,
             response: models.GenerateTrustedPublicKeyResult = None):
        """
        Generate a trusted public key
        """

        if response is None:
           self.majorKey = data.majorKey
           self.sessionId = sessionId
           return data, sessionId

        key_block_verify_intent = models.KeyBlockVerifyIntent(
          key=models.PublicKeyBlock(
            publicKeyBlock=response.publicKeyBlock,
            majorKey=self.majorKey
          )
        )
        key_block_verify = translate_with(
          translators.GDKM_key_block_verify
        )(lambda: None)
        key_block_verify_result = key_block_verify(
          self,
          key_block_verify_intent,
          self.sessionId
        )

        response.kcv = key_block_verify_result.key.kcv

        return response


@bp_keytable.route('/clusters/sessions/<sessionId>/pki/generate-csr')
class KeyBlockGenerateCsrView(ByokView):

    errors = KeySlotsView.errors

    @bp_keytable.json(models.GenerateCsrFromKeyblockIntent)
    @bp_keytable.success(models.Csr)
    @translate_with(translators.GDKM_export_csr)
    def post(self):
        """
        Generate PKCS10 Request from private key block
        """


@bp_keyblock.route('/clusters/sessions/<sessionId>/keyblock/translate')
class KeyBlockTranslateView(ByokView):

    errors = KeySlotsView.errors

    def handle_errors(self, msg):
        # special case for GKBL which returns the key block in the BB tag
        if msg.get('BB') and msg.get('AN') == 'Y':
            return
        return super().handle_errors(msg)

    @bp_keyblock.json(models.KeyBlockTranslateIntent)
    @bp_keyblock.success(models.KeyBlockTranslateResult)
    @translate_with(translators.GDKM_translate_header_3rd, preprocess=True)
    @translate_with(translators.GDKM_translate_kek_2nd, preprocess=True)
    @translate_with(translators.GDKM_translate_usage_1st)
    def post(self):
        """
        Translate key block
        """


@bp_keyblock.route('/clusters/sessions/<sessionId>/keyblock/components')
class KeyBlockComponentsView(ByokView):

    @bp_keyblock.json(models.ComponentGenerationIntent)
    @bp_keyblock.success(models.ComponentGenerationResponse)
    @translate_with(translators.GDKM_create_random_components_final, preprocess=True)
    @translate_with(translators.GDKM_create_random_components_continued, preprocess=True)
    @translate_with(translators.GDKM_create_random_components)
    def post(self):
        """
        Generate random components
        """
