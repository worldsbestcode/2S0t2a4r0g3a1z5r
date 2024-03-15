"""
@file      lib/utils/hapi_parsers.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Parsing functions to supplement Translator request/response mappings
"""

import re
from typing import List, Dict, Any, Iterable

from base.base_exceptions import SerializationError
from string_utils import from_hex


def parse_bool(value: str) -> bool:
    return str(value) == '1'

def parse_reverse_bool(value: str) -> bool:
    return str(value) == '0'

def serialize_bool(value: bool) -> str:
    return '1' if value else '0'

def serialize_reverse_bool(value: bool) -> str:
    return '0' if value else '1'

def parse_csv(csv: str) -> List[str]:
    return csv.split(',') if csv else []

def parse_spaced_csv(csv: str) -> List[str]:
    return csv.split(', ') if csv else []

def serialize_csv(values: list):
    if any(',' in str(value) for value in values):
        raise SerializationError("Invalid character ','")
    return ','.join(values)

def parse_csv_hex(csv: str) -> List[str]:
    return [from_hex(val) for val in parse_csv(csv)]

def parse_csv_bool(csv: str, negate: bool = False) -> List[bool]:
    return [(val == '1') ^ negate for val in parse_csv(csv)]

def parse_csv_int(csv: str) -> List[int]:
    return [int(i) for i in parse_csv(csv)]

def serialize_csv(items: List[str]) -> str:
    return ','.join(items)

def parse_pipe_list(csv: str) -> List[List[str]]:
    return [group.split('|') for group in csv.split(',')]

def parse_key_value_csv(kv: str) -> Dict[str, str]:
    """
    Parse key-value pairs like "key0:val0,key1:val1" to a dict.
    """
    return dict(re.findall('([^:,]*):([^:,]*)', kv))

def serialize_nested_csv(obj_list, csv_sequence):
    """
    Parse a list of objects into an Excrypt object list

    @param  obj_list: A list of objects to be serialized
    @param  csv_sequence: A tuple containing the ordered list of keys
                          for output formatting

    @example
        input:
            obj_list = [{'a':'A1', 'b':'B1', 'c':'C1'}, {'a':'A2', 'b':'B2', 'c':'C2'}]
            csv_sequence = (b, c, a)
        output:
            result = '{B1,C1,A1},{B2,C2,A2}'
    """
    for i, obj in enumerate(obj_list):
        for field in csv_sequence:
            for char in str(obj.get(field, '')):
                if char in '{,}':
                    raise SerializationError(f"Invalid character '{char}' at {i}.{field}")

    result = ''
    formatted_lists = [[str(obj_list[i][item_key]) for item_key in csv_sequence]
                       for i in range(len(obj_list))]

    result_items = []
    for i in range(len(formatted_lists)):
        result_items.append('{' + ','.join(formatted_lists[i]) + '}')

    result = ','.join(result_items)
    return result

def parse_nested_csv(csv, csv_sequence):
    """
    Reverse of serialize_nested_csv.
    """
    return [dict(zip(csv_sequence, group.strip('{}').split(',')))
            for group in csv.split('},{') if group]

def flatten_dict(d, include_nested_keys=False):
    """
    Flatten a nested dictionary into single key:value pairs
    """
    def flat_gen(d):
        if not isinstance(d, dict) and hasattr(d, 'as_dict'):
            d = d.as_dict(False)
        for (k, v) in d.items():
            try:
                v_flat = flat_gen(v)
                for (k_sub, v) in v_flat:
                    k_flat = '%s.%s' % (k, k_sub)
                    if include_nested_keys:
                        yield k, ...
                    yield (k_flat, v)
            except AttributeError:
                yield (k, v)

    return dict(flat_gen(d))

def unpivot_dict(d: Dict[Any, Iterable[Any]]) -> List[Dict[Any, Any]]:
    """
    Reshape/transpose a columnar dict to tabular dicts.
    Example usage:
    in_dict = {
        'a': [1, 2, 3],
        'b': [4, 5, 6],
    }
    out_list = unpivot_dict(in_dict)
    ->
    out_list == [
        {'a': 1, 'b': 4},
        {'a': 2, 'b': 5},
        {'a': 3, 'b': 6},
    ]
    """
    return [dict(zip(d, val)) for val in zip(*d.values())]


def pivot_dict(dict_list: Iterable[Dict[Any, Any]]) -> Dict[Any, List[Any]]:
    """
    Reshape/transpose tabular dicts to a columnar dict, reverse of unpivot_dict.
    """
    # return MultiDict(chain.from_iterable(map(dict.items, l))).to_dict(False)
    out = {}
    for dict_ in dict_list:
        for key, val in dict_.items():
            out.setdefault(key, []).append(val)
    return out


def parse_csv_list(s: str):
    """
    Parse Excrypt list into nested list

    @param  s: Excrypt list

    @example
        input:
            s='{None,Individual,Container,Recursive},{None,Individual}'
        output:
            result=[["None", "Individual", "Container", "Recursive",], ["None", "Individual"]]
    """
    return [item.split(",") for item in s[1:-1].split("},{") if item]


def vectorized(fn, *args, **kwargs):
    def wrapped(iter_):
        return [fn(val, *args, **kwargs) for val in iter_]
    return wrapped
