"""
@file      byok/byok_views.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
A server interface to communicate with a Guardian
"""

from multiprocessing import BoundedSemaphore
import typing

import gevent
from flask_login import current_user

from lib.utils.container_filters import first
from lib.utils.fx_decorators import singledispatchmethod
from lib.utils.data_structures import ExcryptMessage
import rk_host_application.rk_host_application_server_interface as rkasi

if typing.TYPE_CHECKING:
    from lib.auth.user import User
    from lib.comm.middleware_context import MiddlewareContext
    current_user: User


class ContextLocalData:
    """Extra data associated with an apps session"""
    def __init__(self):
        self.keyslot_cache = {}
        self.session_cache: typing.Dict[str, bool] = {}
        self.keyslot_lock = BoundedSemaphore(1)


class ByokServerInterface(rkasi.RKHostApplicationServerInterface):
    def __init__(self, program):
        super().__init__(program)
        self._context_locals: typing.Dict[str, ContextLocalData] = {}

    @property
    def _context_token(self) -> str:
        """Get a token that is unique per RK connection, to differentiate users"""
        assert current_user.context
        return current_user.context.token
    @property
    def _keyslot_cache(self):
        return self._context_locals.setdefault(self._context_token, ContextLocalData()).keyslot_cache
    @property
    def _keyslot_lock(self):
        return self._context_locals.setdefault(self._context_token, ContextLocalData()).keyslot_lock
    @property
    def _session_cache(self):
        return self._context_locals.setdefault(self._context_token, ContextLocalData()).session_cache

    @singledispatchmethod
    def send_msg(self, msg, *, context: typing.Optional['MiddlewareContext'] = None) -> typing.Any:
        raise NotImplementedError()

    @send_msg.register(tuple)
    @send_msg.register(list)
    def _send_msgs(self,
                   msgs: typing.Sequence[typing.Optional[ExcryptMessage]],
                   *,
                   context: 'MiddlewareContext' = None) -> typing.Sequence[typing.Optional[ExcryptMessage]]:
        """Send a list of ExcryptMessages in parallel, responses match input order, or re-raises"""
        # Probably safer to raise than return an empty list
        if not msgs:
            raise ValueError('Nothing to send')
        # Only one message to send? just use this thread
        if len(msgs) == 1:
            return [self._send_msg(msgs[0], context=context)]

        context = context or current_user.context
        response = [gevent.spawn(self.send_msg, msg, context=context) if msg else None for msg in msgs]
        threads = list(filter(None, response))
        gevent.joinall(threads)

        for thread in threads:
            if thread.exception:
                raise thread.exception
        error_thread = first(threads, key=lambda thread: thread.exception is not None)
        if error_thread:
            raise typing.cast(BaseException, error_thread.exception)

        return [None if thread is None else typing.cast(ExcryptMessage, thread.value) for thread in response]

    @send_msg.register(ExcryptMessage)
    def _send_msg(self,
                  msg: ExcryptMessage,
                  *,
                  context: 'MiddlewareContext' = None) -> ExcryptMessage:
        response = self.conn_handler.send_synch(context=context or current_user.context,
                                                message=msg.getText(sanitized=True))
        if not isinstance(response, (str, bytes)):
            response = response[0]
        return ExcryptMessage(response)

    @send_msg.register(str)
    def _send_msg_raw(self, msg: str, *, context: 'MiddlewareContext' = None) -> str:
        return self._send_msg(ExcryptMessage(msg), context=context).getText()

    @send_msg.register(type(None))
    def _ignore_msg(self, msg: None, *, context: 'MiddlewareContext' = None) -> None:
        pass

    def _get_key_table(self, session_id: str, key_type: int) -> 'KeyTable':
        key_table = self._keyslot_cache.get((session_id, key_type))
        if key_table is None:
            from byok.utils.key_table import KeyTable
            key_table = KeyTable(self, session_id, key_type)
            key_table.table
            self._keyslot_cache[(session_id, key_type)] = key_table
        return key_table

    def query_keyslots(self, session_id: str, key_type: int, search: str, order_by: str, ascending: bool, empty: bool):
        key_table = self._get_key_table(session_id, key_type)

        result = key_table.search(substr=search, order_by=order_by, ascending=ascending, empty=empty)

        self._cleanup_keyslot_cache()

        return result

    def _cleanup_keyslot_cache(self):
        with self._keyslot_lock:
            for session_and_type, key_table in tuple(self._keyslot_cache.items()):
                if key_table.is_expired:
                    del self._keyslot_cache[session_and_type]

    def invalidate_keyslot_cache(self, session_id: str, key_type: int):
        with self._keyslot_lock:
            self._keyslot_cache.pop((session_id, key_type), None)

    def session_is_gp_mode(self, session_id: str):
        gp_mode = self._session_cache.get(session_id, None)
        if gp_mode is None:
            response = self.send_msg(ExcryptMessage({
                'AO': 'GDGD',
                'OP': 'read-features',
                'SI': session_id,
            }))
            features = response.get('BO', '').split(',')
            if features:
                gp_mode = 'GP' in features
                self._session_cache[session_id] = gp_mode

        return gp_mode
