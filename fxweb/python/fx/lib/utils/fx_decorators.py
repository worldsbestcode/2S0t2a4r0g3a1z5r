"""
@file      fx_decorators.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021
"""

import itertools
import functools
import math
import time
from typing import Any, Callable, Tuple, TypeVar, Union


_T = TypeVar("_T")


class RetryOnException:
    """
    Decorate a function to make invocations repeat until successful
    """
    def __init__(self, max_attempts=None, catch=(Exception,), logger=None, log_msg=''):
        self.max_attempts = max_attempts or math.inf
        self.catch = catch
        self.logger = logger or str
        self.log_msg = log_msg

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in itertools.count(1):
                try:
                    return func(*args, **kwargs)
                except self.catch if attempt < self.max_attempts else () as e:
                    self.logger(self.log_msg.format(attempt=attempt, exception=e))
                    time.sleep(self.retry_delay(attempt))
        return wrapper

    def retry_delay(self, attempt: int) -> float:
        """
        Smoothly scale retry delay in a sigmoid shape, up to a limit
        """
        lower = 1  # wait at least 1 second
        upper = 60  # wait no more than 60 seconds
        scaling = 20  # scale up to upper bound over about 20 attempts
        if attempt >= scaling:
            return upper
        return lower + .5 * (upper - lower) * (1 - math.cos(math.pi * attempt / scaling))


def singledispatchmethod(fn):
    """
    Single-dispatch generic method descriptor.

    Wraps singledispatch to use second arg for class methods (since 1st arg would be self)
    """
    # TODO(@dneathery): when upgraded to Python 3.8+, use stdlib version
    dispatch_wrapped = functools.singledispatch(fn)
    def wrapper(*args, **kwargs):
        cls = type(args[1])
        return dispatch_wrapped.dispatch(cls)(*args, **kwargs)
    functools.update_wrapper(wrapper, fn)
    wrapper.register = dispatch_wrapped.register
    wrapper.registry = dispatch_wrapped.registry
    wrapper.dispatch = dispatch_wrapped.dispatch
    return wrapper


def __dataclass_transform__(
        *,
        eq_default: bool = True,
        order_default: bool = False,
        kw_only_default: bool = False,
        field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]:
    """Decorate a metaclass definition to annotate that it constructs a dataclass"""
    return lambda fn: fn  # Don't actually do anything at runtime, we're just adding type hints
