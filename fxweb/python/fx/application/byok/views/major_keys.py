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

import byok.models.keys as keys_models
import byok.models.major_keys as models
import byok.translators.major_keys as translators
from byok import BaseResponse, Blueprint, ByokView, translate_with
from byok.byok_enums import MAJOR_KEY_CONSTS


bp = Blueprint(name='Major Key Management')


@bp.route(f'/clusters/sessions/<sessionId>/major-keys')
class MajorKeysView(ByokView):

    errors = {
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
        # skip this error since we're querying for all the major keys:
        '.*ILLEGAL INDEX DATA': 200,
        '.*INVALID MESSAGE LENGTH': 200,  # FW-9413
        # skip this error since we can still return the SKEY rsp even if VPKD fails
        'FAILED TO GET CSKL SESSION OF SLAVE': 200,
        # skip this error so we can check if the VMK/FTK are available
        'VALUE OUT OF RANGE': 200,
    }

    @bp.success(models.MajorKeysInfo)
    @translate_with(translators.GDKM_major_keys_status)
    def get(self):
        """
        List major keys status
        """


@bp.route(f'/clusters/sessions/<sessionId>/major-keys/<any({",".join(MAJOR_KEY_CONSTS.values())}):majorKey>')
class MajorKeyView(ByokView):

    errors = {
        'FIELD OUT OF RANGE': 400,
        'VALUE OUT OF RANGE': 400,
        'USER NOT LOGGED IN': 401,
        'INSUFFICIENT PERMISSION': 403,
        'SESSION NOT FOUND': 404,
        'KEY TABLE UPDATE IN PROGRESS PLEASE WAIT': 503,
        # don't count as an error ANY;BBN; or BBY; (RMMQ response, not actually failure):
        'Y': 200,
        'N': 200,
    }

    @bp.params(models.MajorKeyEraseIntent)
    @bp.success(BaseResponse)
    @translate_with(translators.GDKM_delete_loaded_or_partial_major_key)
    def delete(self):
        """
        Erase partially-loaded or fully-loaded major key
        """


@bp.route(f'/clusters/sessions/<sessionId>/major-keys/<any({",".join(MAJOR_KEY_CONSTS.values())}):majorKey>/fragments')
class MajorKeysFragmentsView(ByokView):

    errors = MajorKeyView.errors

    @bp.success(keys_models.KeyFragments)
    @bp.json(models.GenerateMajorKeyFragmentsIntent)
    @translate_with(translators.GDKM_create_majorkey_fragments, preprocess=True)
    @translate_with(translators.GDKM_create_majorkey_fragments_initial)
    def post(self):
        """
        Generate random fragments that can combine to a major key
        """


@bp.route(f'/clusters/sessions/<sessionId>/major-keys/<any({",".join(MAJOR_KEY_CONSTS.values())}):majorKey>/randomize')
class MajorKeyRandomizeView(ByokView):

    errors = MajorKeyView.errors

    @bp.success(keys_models.KeyFragments)
    @bp.json(models.GenerateMajorKeyFragmentsIntent)
    @translate_with(translators.GDKM_randomize_major_key)
    def post(self):
        """
        Randomize major key and return its new value as fragments
        """


@bp.route(f'/clusters/sessions/<sessionId>/major-keys/<any({",".join(MAJOR_KEY_CONSTS.values())}):majorKey>/switch')
class MajorKeysSwitchView(ByokView):

    errors = MajorKeyView.errors

    @bp.success(BaseResponse)
    @translate_with(translators.GDKM_switch_major_key)
    def post(self):
        """
        Replace major key with KEK and translate the key table
        """
