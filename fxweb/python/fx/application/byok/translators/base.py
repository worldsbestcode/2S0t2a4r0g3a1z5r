"""
@file      byok/translators/base.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Base module for byok conversion functions
"""

import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from lib.utils.data_structures import ExcryptMessage

    from byok import Model


class ByokTranslator(ABC):
    def __call__(self, msg_sender, *args, **kwargs):
        req_msg = self.serialize(*args, **kwargs)
        rsp_msg = msg_sender(req_msg)
        return self.parse(rsp_msg)

    @staticmethod
    @abstractmethod
    def serialize(*args) -> typing.Union['ExcryptMessage', 'list[ExcryptMessage]']:
        pass

    @typing.overload
    @staticmethod
    @abstractmethod
    def parse(msg: 'list[ExcryptMessage]') -> 'Model':
        ...

    @typing.overload
    @staticmethod
    @abstractmethod
    def parse(msg: 'ExcryptMessage') -> 'Model':
        ...

    @staticmethod
    @abstractmethod
    def parse(msg):
        raise NotImplementedError()
