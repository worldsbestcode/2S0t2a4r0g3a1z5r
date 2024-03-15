"""
Copyright Futurex LP
Credits Lilith Neathery
"""

import functools
from typing import Any, Callable, Tuple, TypeVar, Union

_T = TypeVar("_T")

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
