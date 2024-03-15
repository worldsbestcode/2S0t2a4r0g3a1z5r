"""
@file      token_context.py
@author    David Neathery (dneathery@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Metadata for token-authenticated connections
"""

import time

from flask import jsonify
from gevent.lock import BoundedSemaphore
from werkzeug.exceptions import Unauthorized

from lib.utils.data_structures import ExcryptMessage
from middleware_context import MiddlewareContext


class TokenContext(MiddlewareContext):
    """
    Keeps track of information for token-authenticated connections
    """
    def __init__(self, to_address, synch_req_tag='AG', synch_resp_tag='AG'):
        self.to_address = to_address
        self.synch_req_tag = synch_req_tag
        self.synch_resp_tag = synch_resp_tag
        self.token = None
        self.lock = BoundedSemaphore(1)
        self.access_time = time.time()
        self.in_use = 0
        self.connected = False

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.token is not None

    def add_to_request(self, request, token):
        """
        Insert JWT into ExcryptMessage
        """
        msg = ExcryptMessage(request)
        msg.setFieldAsString('JW', token)
        request = msg.getText()
        return request

    def update_from_response(self, response, token):
        """
        Update internal metadata with an Excrypt response
        """
        msg = ExcryptMessage(response)
        # if we failed to authenticate, continue sending the token:
        if msg.getField('JW') == 'N':
            self.token = None
            if msg.getField('ER') == 'User is already logged into this session.':
                # May have tried to login under group that requires more than 1 login,
                # Thus this connection is stuck in a partially-logged-in state. Raise
                # so that the connection can be closed and not re-used.
                response = {'status': 'Failure', 'message': 'Not fully logged in'}
                raise Unauthorized(www_authenticate='Bearer', response=jsonify(response))
        else:
            self.token = token
