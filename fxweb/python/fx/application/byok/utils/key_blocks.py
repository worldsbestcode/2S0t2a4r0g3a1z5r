"""
@file      byok/utils/key_blocks.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Utilities for managing key blocks
"""

from typing import Optional

from byok.models.keys import KeyBlockStr, Tr31KeyBlockDetails


def to_hex(val: Optional[int]) -> Optional[str]:
    if val is None:
        return None
    return f'{val:X}'


def parse_tr31_to_details(key: KeyBlockStr) -> Tr31KeyBlockDetails:
    if len(key) != int(key[1:5]):
        raise ValueError('Invalid TR-31 key block')

    opt_blocks = []
    cursor = 16
    num_opt_blocks = int(key[12:14])
    for _ in range(num_opt_blocks):
        id_ = key[cursor : cursor+2]
        end_pos = cursor + 4 + int(key[cursor+2 : cursor+4], 16)
        value = key[cursor+4 : end_pos]
        cursor = end_pos
        opt_blocks.append(Tr31KeyBlockDetails.OptionalBlock(id=id_, value=value))

    return Tr31KeyBlockDetails(
        header=key[0:cursor],
        version=key[0],
        usage=key[5:7],
        algorithm=key[7],
        modeOfUse=key[8],
        keyVersion=key[9:11],
        exportability=key[11],
        optionalBlocks=opt_blocks,
    )
