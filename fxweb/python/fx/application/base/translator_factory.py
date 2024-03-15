"""
@file      translator_factory.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
A factory for the translators the MethodViews look up
"""

import kmes.kmes_translators
import regauth.regauth_translators


Translators = {
    'KMES': kmes.kmes_translators.map_translators(),
    'RA': regauth.regauth_translators.map_translators(),
}


class TranslatorFactory(object):
    @staticmethod
    def get_translator(translator_type, translator_category, translator_operation):
        selected_translators = {}
        translator = None

        # Find translator type
        if translator_type in Translators:
            selected_translators = Translators[translator_type]

        # Find translator operation category
        if translator_category in selected_translators:
            selected_translators = selected_translators[translator_category]

        # Find translator operation
        if translator_operation in selected_translators:
            translator = selected_translators[translator_operation]

        if not translator:
            raise NotImplementedError(f'{translator_type}.{translator_category}.{translator_operation}')

        return translator
