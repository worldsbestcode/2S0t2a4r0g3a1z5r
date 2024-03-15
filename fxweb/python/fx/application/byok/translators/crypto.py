"""
@file      byok/translators/crypto.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Conversion functions for cryptography operations
"""

from lib.utils.data_structures import ExcryptMessage

from byok import ByokTranslator

class RAND(ByokTranslator):
    @staticmethod
    def serialize(num_bytes: int) -> ExcryptMessage:
        return ExcryptMessage(f'[AORAND;AL{num_bytes};]')

    @staticmethod
    def parse(msg: ExcryptMessage) -> bytes:
        return bytes.fromhex(msg['AK'])
