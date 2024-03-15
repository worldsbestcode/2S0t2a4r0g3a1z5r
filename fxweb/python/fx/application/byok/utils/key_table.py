"""
@file      byok/utils/key_table.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Utilities for managing cluster key tables
"""

import enum
import sys
import time
from functools import partial, reduce, wraps
from operator import attrgetter
from typing import Any, Callable, Iterable, Optional, Sequence, Tuple

import gevent
from flask_login import current_user

from lib.utils.data_structures import ExcryptMessage

from byok.models.keys import KEY_TABLE_TYPES, KeySlotSummary
from byok.byok_enums import KEY_USAGE_ASYM_FLAGS, KEY_USAGE_FLAGS, KEY_USAGE_SYM_FLAGS, MAJOR_KEY_CONSTS, SEC_USAGE_FLAGS

if sys.version_info >= (3, 6):
    OrderedDict = dict  # faster , already ordered
else:
    from collections import OrderedDict

MergedSearchStr = str


KEY_TYPE_CONSTS = {
    '0': 'Empty',
    '1': 'DES',
    '2': '2TDES',
    '3': '3TDES',
    'A': 'AES-128',
    'B': 'AES-192',
    'C': 'AES-256',
    'D': 'Diebold',
    'R': 'RSA-512',
    'r': 'RSA-512 (Public)',
    'S': 'RSA-1024',
    's': 'RSA-1024 (Public)',
    'T': 'RSA-2048',
    't': 'RSA-2048 (Public)',
    'U': 'RSA-3072',
    'u': 'RSA-3072 (Public)',
    'V': 'RSA-4096',
    'v': 'RSA-4096 (Public)',
    'E': 'ECC',
    'e': 'ECC (Public)',
    'X': 'Certificate',
}


def fw_multi_key_usage_to_name(usage_str: str) -> Tuple[str, ...]:
    result = tuple(KEY_USAGE_FLAGS.get(flag, 'Unknown') for flag in usage_str)
    return result

def fw_multi_key_usage_from_name(usages: Optional[Iterable[str]]) -> Optional[str]:
    """Convert list of human-readable key usages to multi-usage str"""
    if usages is None:
        return None
    return ''.join(flag for flag, usage in KEY_USAGE_FLAGS.items() if usage in usages) or None

def fw_sym_key_usage_from_name(usages: Optional[Iterable[str]]) -> Optional[str]:
    """Convert list of human-readable key usages for a symmetric key to str"""
    if usages is None:
        return None
    usages = usages and sorted(usages)
    for flag, names in KEY_USAGE_SYM_FLAGS.items():
        if names == usages:
            return flag and flag.upper()

def fw_asym_key_usage_from_name(usages: Optional[Iterable[str]]) -> Optional[str]:
    """Convert list of human-readable key usages for a symmetric key to str"""
    if usages is None:
        return None
    usages = usages and sorted(usages)
    for flag, names in KEY_USAGE_ASYM_FLAGS.items():
        if names == usages:
            return flag

def fw_multi_sec_usage_to_name(usage_str: str) -> Tuple[str, ...]:
    usage = int(usage_str, base=16)
    result = tuple(name for flag, name in SEC_USAGE_FLAGS if usage & flag)
    return result

def fw_multi_sec_usage_from_name(usages: Optional[Iterable[str]]) -> Optional[str]:
    """Convert list of human-readable security usages to hex"""
    if usages is None:
        return None
    if not usages:
        return '0'
    return f'{reduce(int.__or__, (flag for flag, name in SEC_USAGE_FLAGS if name in usages), 0):X}'


def split_kv(csv: str, _, parse: Callable[[str], Any] = lambda _: _) -> Iterable[Tuple[int, str]]:
    for k_v in csv.split(','):
        if k_v:
            k, _, v = k_v.partition(':')
            yield int(k), parse(v)
    return


def split_bitmap(bitmap: str, offset: int, parse: Callable[[str], str]):
    # the one-char-per-key type, not the bit type
    for slot, slot_value in enumerate(bitmap, start=offset):
        value = parse(slot_value)
        if value is not None:
            yield slot, value
    return


def split_keyType(bitmap: str, offset: int):
    for slot, slot_value in enumerate(bitmap, start=offset):
        key_type = KEY_TYPE_CONSTS.get(slot_value, 'Unknown')
        if key_type == 'Empty':
            obj = KeySlotSummary(
                slot=slot,
                type=key_type,
                kcv=None,
                label=None,
                modifier=None,
                majorKey=None,
                usage=None,
                securityUsage=None,
            )
        else:
            obj = KeySlotSummary(slot=slot, type=key_type)
        yield slot, obj


class GpkmMode(enum.IntEnum):
    keyType = 0
    # These line up with the names in a KeySlotSummary
    kcv = 3
    label = 4
    modifier = 5
    majorKey = 9
    usage = 10
    securityUsage = 11


class KeyTable:

    xd_tag_parsers = {
        GpkmMode.keyType: split_keyType,
        GpkmMode.kcv: split_kv,
        GpkmMode.label: split_kv,
        GpkmMode.modifier: partial(split_kv, parse=partial(int, base=16)),
        GpkmMode.majorKey: partial(split_bitmap, parse=MAJOR_KEY_CONSTS.get),
        GpkmMode.usage: partial(split_kv, parse=fw_multi_key_usage_to_name),
        GpkmMode.securityUsage: partial(split_kv, parse=fw_multi_sec_usage_to_name),
    }

    def __init__(self, server_interface: 'ByokServerInterface', session_id: str,
                 table_type: int) -> None:
        self.server_interface = server_interface
        self.session_id = session_id
        self.table_type = table_type
        self.dense_table_size = 25450  # assumed max key slots # for preallocated index
        self.table: OrderedDict[MergedSearchStr, KeySlotSummary] = {}

        self.max_table_age = 120  # when searching, rebuild if older than N seconds
        self.table_build_time = 0

        self.prev_search_results = {}
        self.prev_search_str = ''

    def _query_key_attrs(self, mode: GpkmMode, destination, context: 'MiddlewareContext'):
        parser = self.xd_tag_parsers[mode]
        current_offset = 0
        reached_end_of_table = False
        request = ExcryptMessage(
            f'[AOGDKM;OPlist-keyslots;SI{self.session_id};XA{mode.value};CT{self.table_type};]')
        while not reached_end_of_table:
            request['XC'] = current_offset
            response = self.server_interface.send_msg(request, context=context)

            data = response.get('XD', '')
            if data:
                for slot, value in parser(data, current_offset):
                    destination[slot] = value

            offset_of_next_page = int(response.get('XC', 0))
            reached_end_of_table = offset_of_next_page <= current_offset
            current_offset = offset_of_next_page

    def rebuild_table(self) -> None:
        """Repeatedly call GPKM via GDKM to fill table"""

        table = self.table
        table.clear()

        # Map from an XA tag to key slot to the parsed value for that tag and slot
        destinations = {
            mode: {} if mode == GpkmMode.keyType else [None] * self.dense_table_size
            for mode in GpkmMode
        }

        # Asynchronously fill the destinations with values
        gevent.joinall([
            gevent.spawn(self._query_key_attrs, mode, destination, current_user.context)
            for mode, destination in destinations.items()
        ])

        # Use the key type KeySlotSummary's to be updated in place with all the XA tag values
        table_entries = destinations.pop(GpkmMode.keyType)
        table_values = [(mode.name, values) for mode, values in destinations.items()]

        for slot, entry in table_entries.items():
            for attr_name, values in table_values:
                value = values[slot]
                if value is not None:
                    setattr(entry, attr_name, value)
            # Store it under its "searchable" string
            # Preserves order, table_entries is sorted by key slot # and table is OrderedDict
            search_str = '\0'.join(
                ('/'.join(value) if isinstance(value, (tuple, list)) else str(value)).lower()
                for value in vars(entry).values()
                if value is not None
            )
            table[search_str] = entry

        # All done, update table age
        self.table_build_time = time.time()

    def search(self, substr: str, order_by: str, ascending: bool, empty: bool) -> Sequence[KeySlotSummary]:
        """Naively search the table for a substring in one of its fields, maybe rebuild if old"""

        if self.is_expired:
            self.rebuild_table()

        # do case-insensitive search
        substr = substr.lower()

        # maybe use a suffix array / trie for speeds instead of searching all the "merged" strings
        # for now just cache the previous search result since the user "probably" adds one char
        # at a time so we can narrow it down
        if substr and self.prev_search_str and self.prev_search_str in substr:
            search_space = self.prev_search_results
        else:
            search_space = self.table

        if empty and not substr:
            results = search_space
        elif not empty and not substr:
            results = {_: entry for _, entry in search_space.items() if entry.type != 'Empty'}
        elif empty:
            results = {
                merged_search_str: entry
                for merged_search_str, entry in search_space.items() if substr in merged_search_str
            }
        else:
            results = {
                merged_search_str: entry
                for merged_search_str, entry in search_space.items()
                if entry.type != 'Empty' and substr in merged_search_str
            }

        self.prev_search_str = substr
        self.prev_search_results = results

        return sorted(results.values(), key=attrgetter(order_by), reverse=not ascending)

    @property
    def is_expired(self):
        return self.table_build_time + self.max_table_age < time.time()


def invalidates_keytable_cache(fn):
    """Get a view decorator that invalidates key table cache on success (implies mutation)"""
    # decorating the view method

    @wraps(fn)
    def wrapper(self, *args, sessionId, tableType = None, **kwargs):
        # view function called (handling a request)

        if tableType:
            kwargs['tableType'] = tableType

        view_response = fn(self, *args, sessionId=sessionId, **kwargs)

        if not any(b'Success' in rsp for rsp in view_response.response):
            return view_response

        if tableType is None:
            tables_to_invalidate = KEY_TABLE_TYPES.values()
        else:
            tables_to_invalidate = ( KEY_TABLE_TYPES.get(tableType, 1), )
        for key_type_int in tables_to_invalidate:
            self.server_interface.invalidate_keyslot_cache(sessionId, key_type_int)

        return view_response

    return wrapper
