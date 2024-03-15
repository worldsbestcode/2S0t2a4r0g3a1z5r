"""
@file      base_command.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Interface for using Excrypt commands with a "Translator"
"""

from functools import lru_cache
from typing import Hashable

from lib.utils.data_structures import ExcryptMessage


class BaseCommand:
    """
    Base class for handling Excrypt commands.

    Override request or response hooks for custom behaviour.
    """

    name = ''

    def __init__(self, server_interface):
        self.server_interface = server_interface
        assert self.name

    def send(self, data: dict) -> dict:
        # Default behavior is to send the translated request data
        request = self.build_message(data)
        request = self.preprocess_request(request)
        response = self.make_request(request)
        response = self.finalize_response(response)
        return response

    def build_message(self, data: dict) -> ExcryptMessage:
        result = ExcryptMessage()
        # Add command tag first so it appears first in the message (Python 3.6+)
        result['AO'] = self.name
        result.update(data)
        return result

    def preprocess_request(self, request):
        # Default behaviour does nothing
        return request

    def make_request(self, request):
        response = self.server_interface.send(request.getText())
        return ExcryptMessage(response)

    def finalize_response(self, response):
        # Default behaviour does nothing
        return response


class CachedCommandMixin:
    """
    Mixin class to cache command results.

    Maintains LRU cache on distinct calls to send() for each derived class.
    """

    class SameHash:
        """
        Utility class to clobber dicts.
        """

        def __init__(self, this):
            self.this = this
        def __hash__(self):
            return id(self.this.__class__)
        def __eq__(self, other):
            same_class = isinstance(other.this, self.this.__class__)
            same_interface = other.this.server_interface is self.this.server_interface
            return same_class and same_interface # don't clobber other Commands

    @classmethod
    @lru_cache()
    def _cached_send(cls, args: SameHash, data: Hashable) -> dict:
        # bind to the 'self' hidden from lru_cache and restore data:
        return super(CachedCommandMixin, args.this).send(dict(data))

    def send(self, data):
        return self.__class__._cached_send(
            CachedCommandMixin.SameHash(self), # need to masquerade as a singleton
            frozenset(data.items()) # need to make data dict hashable
            )
