"""
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, L.P. 2018
"""

from collections import deque
from typing import Callable, Iterator, Sequence, TypeVar, Union

_T = TypeVar('_T')


def apply_vec(fn: Callable[[_T], None], arg: Union[_T, Sequence[_T]]):
    """Get a function that applies itself to every element of a sequence (or a single element)"""
    if isinstance(arg, Sequence):
        consume(map(fn, arg))
    else:
        fn(arg)
    return arg


def consume(iterator: Iterator):
    """Repeatedly next an iterator, discarding results, until empty"""
    deque(iterator, maxlen=0)


def filter_none_values(fields):
    """Filter a map of any key that has a value set as None.

    Args:
        fields: The map to filter

    Returns:
        map of filtered key-value pairs
    """
    return {k: v for k, v in fields.items() if v is not None}

def filter_none_recursive(d: dict) -> dict:
    """Deeply filter a collection of any map's key that has a value set as None, in place."""
    if not hasattr(d, '__iter__') or isinstance(d, (str, bytes)):
        return

    recurse = []
    try:
        to_prune = [key for key, value in d.items() if value is None]
        recurse = d.values()
    except (AttributeError, TypeError, ValueError):
        to_prune = []
        recurse = d

    try:
        for key in to_prune:
            del d[key]
    except:
        pass

    for value in recurse:
        filter_none_recursive(value)


def coalesce_dict(d, keys=[], fallback=None):
    result = fallback
    found_keys = list(d.keys() & keys)

    if len(found_keys) > 0:
        result = d[found_keys[0]]

    return result


def dot_notation_get(d, path, default=None):
    try:
        for subpath in path.split('.'):
            d = d[subpath]
    except (TypeError, LookupError):
        return default
    return d


def camel_case_dict(camel_dict):
    keyupdate = {}
    for key in camel_dict.keys():
        split = key.split('_')
        camel_key = split[0] + ''.join(i.title() for i in split[1:])
        if camel_key != key:
            keyupdate[key] = camel_key

        if isinstance(camel_dict[key], dict):
            camel_case_dict(camel_dict[key])

    for key in keyupdate.keys():
        camel_dict[keyupdate[key]] = camel_dict.pop(key)


def snake_case_dict(snake_dict):
    keyupdate = {}
    for key in snake_dict.keys():
        snake_key = ''.join(['_'+i.lower() if i.isupper() else i for i in key]).lstrip('_')
        if snake_key != key:
            keyupdate[key] = snake_key

        if isinstance(snake_dict[key], dict):
            snake_case_dict(snake_dict[key])

    for key in keyupdate.keys():
        snake_dict[keyupdate[key]] = snake_dict.pop(key)


def first(iterable, default=None, key=lambda x: x):
    """
    Return the first truthy value.
    """
    for value in iterable:
        if key(value):
            return value
    return default
