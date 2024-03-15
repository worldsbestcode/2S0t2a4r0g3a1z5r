"""
@file      middleware_context.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Connection meta data information
"""
from gevent.lock import BoundedSemaphore
from asynccomm import synchronized
from itsdangerous import JSONWebSignatureSerializer
import os
import hashlib
import base64

ANONYMOUS_GROUP = '1000'

global ATTEMPT
ATTEMPT=0

def generate_token():
    """
    Generates a cookie safe token
    """
    # Use a multiple of three to avoid any padding
    length = 36
    return base64.b64encode(os.urandom(length)).decode()


class MiddlewareContext(object):
    synch_value = 0
    synch_semaphore = BoundedSemaphore(1)

    """Keeps track of to/from information for Connections """
    def __init__(self, from_address, to_address, config, app, synch_req_tag='AG', synch_resp_tag='AG'):
        """Initialize the message_context
        @param from_addr: an identifier for the from address
        @param to_addr: an identifier for the to address
        @param config: The server config
        """
        self.from_address = from_address
        self.to_address = to_address
        self.config = config
        self.app = app
        self.serializer, self.token, self.encrypted_token, self.csrf_token = self.__generate_session()
        self.synch_req_tag = synch_req_tag
        self.synch_resp_tag = synch_resp_tag
        self.login_info = {}

    def __generate_session(self):
        """
        Generates a unique user id. This id is mac'd so that it cannot be tampered with
        """
        salt = hashlib.sha256(os.urandom(8) + self.config.key).digest()
        token = generate_token()
        serializer = JSONWebSignatureSerializer(self.config.key, salt)
        encrypted_token = serializer.dumps(token).decode()

        csrf_token = generate_token()

        return serializer, token, encrypted_token, csrf_token

    def get_req_synch_tag(self):
        """
        Returns the request synch tag for context
        """
        return self.synch_req_tag

    def get_resp_synch_tag(self):
        """
        Returns the response synch tag for context
        """
        return self.synch_resp_tag

    def is_anonymous(self):
        """Check if anonymous or not
        Returns: true if anonymous false otherwise
        """
        return self.login_info.get('id') == ANONYMOUS_GROUP

    @property
    def user_group_id(self):
        """Retrieve user group ID
        Returns: User group ID (or None)
        """
        return self.login_info.get('id')

    @synchronized(synch_semaphore)
    def inc_synch_value(self, inc_amt=1):
        """
        Increments the synch value associated with the connection
        Note: Global per class so that each connection does not clash with sync ids
        :param inc_amt: Amount to increment by
        """
        MiddlewareContext.synch_value += inc_amt
        new_synch_value = MiddlewareContext.synch_value
        return str(new_synch_value)

    @synchronized(synch_semaphore)
    def get_synch_value(self):
        """
        Returns current synch id value
        :return: Current synch id value
        """
        new_synch_value = MiddlewareContext.synch_value
        return str(new_synch_value)
