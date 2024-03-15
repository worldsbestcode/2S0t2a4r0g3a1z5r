"""
@file      app_sanitize.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Sanitizes the JSON in the request body
"""

import re
from flask import request
from functools import wraps, partial
from werkzeug.datastructures import MultiDict
from marshmallow import ValidationError
import json

def sanitize_request(func, options=["excrypt"]):
    '''
    Decorator for sanitizing the JSON in the request body
    '''
    def sanitize_all(value):
        '''
        Walks through the dict sanitizing all strings found
        '''
        if isinstance(value, dict):
            value = {k:sanitize_all(v) for k, v in value.items()}
        elif isinstance(value, list):
            value = [sanitize_all(v) for v in value]
        elif isinstance(value, str):
            value = sanitize_string(value)
        return value

    def sanitize_string(value):
        '''
        Applies the sanitizing functions in the order the options are set
        '''
        result = value

        for option in options:
            if option == "excrypt":
                result = remove_excrypt_chars(result)

        return result

    @wraps(func)
    def decorated_view(*args, **kwargs):
        '''
        Sanitizes the JSON in the request body before
        calling the actual view that this decorates
        '''
        request_data = request.get_json(silent=True)

        # Sanitize if there is JSON in the request body
        if request_data is not None:
            request_data = sanitize_all(request_data)
            writeRequestJSON(request_data)

        # Call the wrapped function
        return func(*args, **kwargs)

    return decorated_view

def validate_request_json_is_dict(view):
    """
    Decorate a view to check for valide json dict
    """
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            request_data = request.get_json(force=True)
        except ValueError:
            # if user didn't indicate mimetype application/json, get_json would return None
            # so we pass force=True to try to parse and let the view catch any errors in the json
            request.get_json = partial(request.get_json, force=True)
        else:
            if request_data is None:
                writeRequestJSON({})
            elif not isinstance(request_data, dict):
                raise ValidationError("Invalid input type")
            else:
                writeRequestJSON(request_data)

        return view(*args, **kwargs)
    return wrapper

def writeRequestJSON(data):
    '''
    Rewrites the dict used by the request context for get_json
    '''
    # Cached values for ``(silent=False, silent=True)``. Initialized
    # with sentinel values: Tuple[Any, Any] = (Ellipsis, Ellipsis)
    request.__dict__["_cached_json"] = (data, data)

def remove_excrypt_chars(value):
    '''
    Removes reserved characters for Excrypt and Standard messages
    '''
    return re.sub(r"[;\[\]<>]", "", value)

class sanitize_args(object):
    """
    MethodView decorator for sanitizing the query component of a request

    @param multi: Whether to set args to a MultiDict or a dict; default is dict
        Note that multi=True preserves duplicated keys but lookups yield lists,
        while multi=False uses only the first such value and yields strings.
    """
    def __init__(self, multi=False): # instantiate in class decorator list
        self.multi = multi
        self.sanitizer = remove_excrypt_chars

    def __call__(self, function): # when binding to URI via MethodView.as_view
        @wraps(function)
        def wrapper(*view_args, **view_kwargs):
            request.args = self._sanitized(request.args)
            return function(*view_args, **view_kwargs)
        return wrapper
    
    def _sanitized(self, query_params):
        if self.multi:
            result = MultiDict()
            for k, v in query_params.items(True): # don't sanitize keys
                result.add(k, self.sanitizer(v))
        else:
            result = {k:self.sanitizer(v) for k,v in query_params.items(False)}
        return result
