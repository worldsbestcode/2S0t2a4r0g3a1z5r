"""
@file      byok/views/base.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Base view for BYOK APIs
"""

import functools
from re import match
from typing import Dict, Optional, TYPE_CHECKING, Type, Union, cast

from flask.views import MethodView

from base.app_csrf import csrf_required
from lib.utils.container_filters import apply_vec, first

import byok

if TYPE_CHECKING:
    from byok import ByokServerInterface, ByokTranslator
    from lib.comm.middleware_context import MiddlewareContext
    from lib.utils.data_structures import ExcryptMessage


class ByokView(MethodView):

    decorators = [csrf_required]

    errors: Dict[str, int] = {}

    def __init__(self, server_interface: 'ByokServerInterface'):
        super().__init__()
        self.server_interface = server_interface

    def handle_errors(self, msg: 'ExcryptMessage'):
        """Error handling hook, naively breaks out errors to HTTP responses"""
        if msg.success or ('AN' not in msg and msg.get('CN') == 'Y'):
            return

        err_msg = msg.get('ER', msg.message)
        status_code = first((code for pattern, code in self.errors.items() if match(pattern, err_msg)), default=500)
        if status_code and status_code > 299:
            byok.abort(status_code, err_msg)


def translate_with(translator: Union[Type['ByokTranslator'], 'ByokTranslator'],
                   preprocess=False,
                   postprocess=False,
                   handle_errors=True,
                   context: Optional['MiddlewareContext'] = None):
    """Bind a translator to handle request/response parsing for this view"""
    # Handling arguments for decorator before decorating

    if not isinstance(translator, type):
        translator = cast(Type['ByokTranslator'], lambda: translator)

    def get_msg_handler(self):
        # A callable that sends a message and returns a response, and maybe check for any errors
        msg_sender = lambda msg: self.server_interface.send_msg(msg, context=context)
        if handle_errors:
            # If we skipped the message (sent None) then skip the error check too
            check_error_if_msg = lambda msg: msg and self.handle_errors(msg)
            return lambda msg: apply_vec(check_error_if_msg, msg_sender(msg))
        return msg_sender

    def decorator(view_fn):
        # Decorating the view

        # Check we're not decorating an already decorated view, we need to go first:
        assert all(map('__wrapped__'.__eq__, vars(view_fn))), "Put @translate_with at the bottom of the decorators (innermost)"

        @functools.wraps(view_fn)
        def wrapper(self: 'ByokView', *args, **kwargs):
            # Method is called (we are handling a request)

            # Do any preprocessing by calling the view
            if preprocess:
                bound_view_fn = view_fn.__get__(self)
                try:
                    args = bound_view_fn(*args, **kwargs)
                except StopIteration as e:
                    return e.value
                kwargs.clear()

            # Get a fn we can send ExcryptMessages to and get [success] responses [if handle_errors]
            msg_sender = get_msg_handler(self)

            # Translate the request into a response using the translator
            response = translator()(msg_sender, *args, **kwargs)

            # Do any post-processing by calling the view
            if postprocess:
                bound_view_fn = view_fn.__get__(self)
                response = bound_view_fn(response=response)

            return response

        return wrapper

    return decorator
