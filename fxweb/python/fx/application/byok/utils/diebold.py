"""
@file      byok/utils/diebold.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Utilities for managing Diebold tables
"""

import math
from itertools import count
from typing import Callable, List, MutableSequence, Tuple, Union

from byok.models.keys import DieboldTableData


def gen_diebold(random_bytes: bytes) -> DieboldTableData:
    """Generate a Diebold table using the provided random bytes as entropy"""
    # the table is values 0x00-0xFF arranged in a random order, except the first nibble must be 0xC.
    # we want each possible table to be equally likely given the random_bytes are good quality.
    # we'll use the factoradic-permutation method to map each of the possible tables to one number,
    # then randomly generate that number once using discard-if-greater to avoid modulo bias,
    # but since the numbers are so large (255!) we'll only check 1 bit at a time as an optimization.
    # note even though it looks like Fisher-Yates, we're not using that to shuffle directly, as it
    # would require more randint calls, which would require throwing away far, far more random_bytes

    # start with the 0x01-0xFF sorted, all but the initial 0x00 position we will shuffle:
    table = list(range(1, 256))

    # convert the random bytes into a long str of random bits with leading 0's (ex '01100111...')
    bitstring = f'{int.from_bytes(random_bytes, byteorder="big"):0{8*len(random_bytes)}b}'
    # a callable that returns one bit from the bitstring at a time
    get_bit = iter(bitstring).__next__
    get_bit: Callable[[], Union['Literal["0"]', 'Literal["1"]']]

    # use the random bytes to select a random permutation (a lexicographic rank)
    permutation = _diebold_randrange(get_bit)
    # in-place swap the values into the position for that permutation
    _nth_permutation(permutation, table)

    # need to force the first byte to be one of C0 - CF
    # randomly pick a 0-F for the nibble
    second_nibble = int(''.join(get_bit() for _ in range(4)), base=2)
    first_byte = 0xC0 + second_nibble

    # swap the 0x00 we didn't shuffle with wherever the random first_byte happened to be shuffled to
    pos_00 = table.index(first_byte)
    table[pos_00] = 0
    table.insert(0, first_byte)

    return bytes(table)


def _diebold_randrange(get_bit, *, _MAX_BITS: str = f'{math.factorial(255):b}') -> int:
    """Get a random number less than 255!"""
    # _MAX_BITS: binary representation of the max value, 255!, as a str: '111111110101...'
    cursor: int = 0  # position in the _MAX_BITS str that so far has =='d the bits we've checked
    result: List[str] = []  # put <= bits here

    # Find the first bit in the stream that is not equal to _MAX_BITS
    while cursor < len(_MAX_BITS):
        candidate = get_bit()  # retrieve the next bit from the random stream
        if candidate > _MAX_BITS[cursor]:
            # 1 > 0, throw away all the bits we've checked and start over (NIST SP 800-90A "Simple Discard Method")
            result.clear()
            cursor = 0
            continue
        result.append(candidate)
        if candidate < _MAX_BITS[cursor]:
            # 0 < 1, stream will necessarily < 255! so we can use this for our random number
            break
        # bits are equal, we can't be sure whether the stream <= 255! yet, so check the next one
        cursor += 1

    # since we almost certainly hit the break, add remaining less significant bits
    result.extend(get_bit() for _ in range(len(_MAX_BITS) - len(result)))

    # parse the bits into an actual int
    rand_int = int(''.join(result), base=2)
    return rand_int


def _nth_permutation(n: int, vals: MutableSequence[int]) -> None:
    """In-place shuffle a pre-sorted list to the permutation that is n'th lexicographically"""
    for index in _factoradic(n, len(vals)):
        vals.append(vals.pop(index))


def _factoradic(n: int, pad_length: int) -> Tuple[int, ...]:
    """Convert to factorial base, padded up to length (on the left)"""
    if n < 0:
        raise ValueError

    result = []
    radix = count(1)
    while n:
        n, digit = divmod(n, next(radix))
        result.append(digit)

    num_padding = max(pad_length - len(result), 0)

    return (*[0] * num_padding, *reversed(result))
