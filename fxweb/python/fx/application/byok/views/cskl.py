"""
@file      byok/views/major_keys.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2022

@section DESCRIPTION
Views for major key management
"""

from typing import cast

import byok.models.cskl as models
import byok.translators.cskl as translators
import byok.translators.major_keys as mk_translators
from byok import Blueprint, ByokView, abort, translate_with
from byok.byok_enums import MAJOR_KEY_CONSTS


bp = Blueprint(name='Partial Key Load')


@bp.route(f'/clusters/sessions/<sessionId>/keyload/clearkey-sessions')
class KeyLoadSessionView(ByokView):

    errors = {
        'FIELD OUT OF RANGE': 400,
        'VALUE OUT OF RANGE': 400,
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
    }

    @bp.json(models.CreateKeyLoadSessionIntent)
    @bp.success(models.KeyLoadSessionDetails)
    @translate_with(translators.GDKM_create_ephemeral_key)
    def post(self):
        """
        Create key loading session
        """


@bp.route(f'/clusters/sessions/<sessionId>/keyload/auth-receipt')
class CreatePartialKeyDataView(ByokView):

    errors = {
        'FIELD OUT OF RANGE': 400,
        'VALUE OUT OF RANGE': 400,
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
    }

    @bp.json(models.CPKDLoadData)
    @bp.success(models.PartialKeyLoadResponse)
    @translate_with(translators.GDKM_create_cskl_receipt)
    def post(self):
        """
        Upload partial key data
        """


@bp.route(f'/clusters/sessions/<sessionId>/major-keys/<any({",".join(MAJOR_KEY_CONSTS.values())}):majorKey>/partial-key-load')
class MajorKeyLoadView(ByokView):

    errors = {
        'FIELD OUT OF RANGE': 400,
        'VALUE OUT OF RANGE': 400,
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
        # skip this error since we're speculatively checking if an upload already exists
        '.*ILLEGAL INDEX DATA': 200,
        '.*INVALID MESSAGE LENGTH': 200,  # FW-9413
        # skip these error since we might call RMMQ and it gives the deleted result in BB
        'Y': 200,
        'N': 200,
    }

    @bp.json(models.HPKDLoadData)
    @bp.success(models.PartialKeyLoadResponse)
    @translate_with(translators.GDKM_hpkd, preprocess=True, postprocess=True)
    def post(self, obj: models.HPKDLoadData = ..., sessionId: str = ..., majorKey: str = ..., response: models.PartialKeyLoadResponse = ...):
        """
        Upload partial major key data
        """
        if response is ...:  # preprocessing
            # figure out if there's an existing key load session and get the memqueue index to reuse:
            get_session = translate_with(translators.GDKM_read_cskl_session)(lambda: ...)
            self.vpkd_info = get_session(self, sessionId=sessionId, majorKey=majorKey)
            self.session_id = sessionId
            self.major_key = majorKey

            # lines up with *args to GDKM_hpkd.serialize:
            return obj, sessionId, majorKey, self.vpkd_info

        # postprocessing
        if response.have and response.want == response.have:
            self.recombine(response)
        return response

    def recombine(self, response: models.PartialKeyLoadResponse):
        # mq now has all the parts needed, trigger KCCR;CS to actually store the major key
        finalize = translate_with(translators.GDKM_finalize_hpkd, handle_errors=False)(lambda: ...)
        kcv = finalize(self, sessionId=self.session_id, vpkd=self.vpkd_info)

        if kcv:  # success
            # include the combined kcv
            response.kcv = cast(models.KeyChecksum, kcv)
            return

        # recombine failed, so reset the cskl session so they can start over
        cleanup = translate_with(mk_translators.GDKM_delete_cskl_session)(lambda: ...)
        cleanup(self, sessionId=self.session_id, majorKey=self.major_key)
        abort(400, 'Failed to recombine key parts. Key load aborted.')
