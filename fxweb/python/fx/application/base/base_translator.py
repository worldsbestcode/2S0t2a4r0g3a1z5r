"""
@file      base_translator.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Interface for translating HTTP requests to commands
"""
import typing
from functools import partial, reduce

from werkzeug.datastructures import MultiDict

from base.base_exceptions import SerializationError
from lib.utils.data_structures import ExcryptMessage, ExcryptMessageResponse
from lib.utils.container_filters import dot_notation_get


class BaseTranslator(object):
    """
    Interface for translating HTTP requests to commands.

    @param server_interface: The interface that will send the commands.
    @param command_category: The category of the Command. Ex: 'Config'
    @param command_name: The specific command to use. Ex: 'TIME'
    @param request_map: A dictionary mapping JSON keys to command tags.
        Values can be a string encoding of the target command tag or tuple
        with that string and a callable parser to modify the request string.
        Example usage: Suppose Request to set system time has:
        requestData = {'config': {'setTime': '2012-10-31 00:00:00'}}
        Expects to generate message [AOTIME;TI2012-10-31 00:00:00;]
        request_map = {'config.setTime': 'TI'}
    @param response_map: A dictionary mapping response tags to JSON keys.
        Values can be string encoding of the target JSON key or tuple with
        that string and a callable parser to modify the response string.
        Example usage:
        response_map = {
        'TI': ('time.utc', int)                     # convert to int
        'TZ': 'time.timezone'                       # leave value unmodified
        'LS': ('time.tzs', lambda s: s.split(','))  # convert csv into list
        }
    @param fixed_values: A dict mapping request command tags to fixed values.
    @attribute request_schema: A marshmallow schema used to validate the request.
    """

    _output_type = ExcryptMessageResponse

    def __init__(self, server_interface, command_category, command_name, request_map=None, response_map=None, fixed_values=None):
        super(BaseTranslator, self).__init__()
        self.server_interface = server_interface

        self.command_category = command_category
        self.command_name = command_name

        self.request_map = request_map
        self.response_map = response_map

        self.fixed_values = fixed_values

    def validateRequest(self, request):
        request_schema = getattr(self, 'request_schema', None)
        if request_schema:
            # Schema.load() will raise ValidationError if request does not pass validation
            request = request_schema.load(request)

        return request

    def preprocess_request(self, request):
        """
        Hook to handle a raw request before it is translated and sent to the interface.
        """

        return request

    def translateRequest(self, request):
        self.raw_request = request
        # Default result is the un-translated request
        result = request

        if self.request_map is not None:
            result = self._output_type()

            for json_key in self.request_map:
                raw_value = dot_notation_get(request, json_key, default=Ellipsis)  # could be null
                try:
                    tag, value = self._translate_field(raw_value, self.request_map, json_key)
                except SerializationError as e:
                    e.field_name = json_key
                    raise
                except Exception:
                    raise SerializationError(field_name=json_key)
                if value in (None, Ellipsis):
                    continue  # field missing from request or explicitly ignored, skip

                invalid = ExcryptMessage.check_invalid(value)
                if invalid:
                    raise SerializationError(f"Invalid character '{invalid}'", json_key)

                self._add_to_dict(result, tag, value)

        if self.fixed_values:
            result.update(self.fixed_values)

        self.translated_request = result
        return result

    def makeRequest(self, request):
        return self.server_interface.send_command(
            self.command_category,
            self.command_name,
            request
        )

    def translateResponse(self, response):
        self.raw_response = response
        result = response

        # Translation is skipped if there is no map dict
        if self.response_map is not None:
            result = self._output_type()

            for tag in self.response_map:
                raw_value = dot_notation_get(response, tag, default=Ellipsis)

                if raw_value in (None, Ellipsis):
                    continue  # field missing from response or explicitly ignored, skip

                destination, value = self._translate_field(raw_value, self.response_map, tag)
                self._add_to_dict(result, destination, value)

        self.translated_response = result
        return result

    def finalize_response(self, response: ExcryptMessageResponse) -> ExcryptMessageResponse:
        """
        Hook to handle a translated response before it is returned to the invoking context.
        """

        return response

    def translate(self, request):
        calls = [
            self.validateRequest,
            self.preprocess_request,
            self.translateRequest,
            self.makeRequest,
            self.translateResponse,
            self.finalize_response,
        ]

        return reduce(lambda result, call: call(result), calls, request)

    def __call__(self, request):
        return self.translate(request)

    # Support dot notation for dict key mapping
    def _add_to_dict(self, input_dict, accessor, value, clobber=False):
        index_dict = input_dict
        keys = accessor.split('.')

        # Seek to the nested dict
        for key in keys[:-1]:
            # If the parent in the path doesn't already exist, create it
            if not key in index_dict:
                index_dict[key] = {}

            # Else, we found something in this part of the path...
            else:
                # When "clobber" is "True", ensure it's a dict so we can continue
                if clobber and not type(index_dict[key]) is dict:
                    index_dict[key] = {}

            # Advance the "index_dict" reference one level deeper
            index_dict = index_dict[key]

        # Set the value
        index_dict[keys[-1]] = value

    @staticmethod
    def _translate_field(value, mapping, field):
        """
        Translate a value if mapping supplies a translator for that field.
        """
        map_to = mapping[field]
        if value is not Ellipsis and callable(map_to):
            return map_to(value, field)
        elif not isinstance(map_to, tuple):  # if mapping value is tuple, it may need to be translated
            return map_to, value  # no translator for this field so just return raw value

        destination, *parsers = map_to
        if len(parsers) == 0:  # no parser, may have made this a tuple by mistake
            return destination, value
        for parser in parsers:
            if type(parser) is str:
                value = parser  # maps to a fixed value
            elif value is Ellipsis:
                value = None
                break
            elif callable(parser):
                value = parser(value)
            elif isinstance(parser, typing.Mapping):
                value = parser[value]
            else:
                raise NotImplementedError('Not a supported parser type' + repr(parser))

        return destination, value


class MultiCommandTranslator(BaseTranslator):
    """
    Interface for translating HTTP requests to multiple commands.
    """

    def makeRequest(self, mw_req):
        mw_resp = ExcryptMessageResponse()
        for category, name in zip(self.command_category, self.command_name):
            rk_resp = self.server_interface.send_command(category, name, mw_req)
            rk_resp = self.on_receipt(rk_resp)
            mw_resp.update(rk_resp)
        return mw_resp

    def on_receipt(self, response):
        """
        Hook to handle a raw partial response before another command is issued.
        """

        return response

class SequentialTranslator(BaseTranslator):

    def __init__(self, server_interface):
        self.server_interface = server_interface
        self.raw_request = []
        self.translated_request = []
        self.raw_response = []
        self.translated_response = []
        self.fixed_values = {}

    def translate(self, request):
        response = ExcryptMessageResponse()
        request = self.validateRequest(request)
        request = self.preprocess_request(request)

        params = zip(*zip(*self.commands), self.request_maps, self.response_maps)
        for self.command_category, self.command_name, self.request_map, self.response_map in params:
            partial_request = self.translateRequest(request)
            partial_response = self.makeRequest(partial_request)
            self.translateResponse(partial_response, response)
            failure_message = self.check_failure(response)
            if failure_message is not None:
                return failure_message

        response = self.finalize_response(response)
        return response

    def check_failure(self, response):
        if response.get('message') or response.get('status', 'Y') != 'Y':
            return response
        return None

    def translateResponse(self, response, previous_response=None):
        self.raw_response = response
        result = response

        # Translation is skipped if there is no map dict
        if self.response_map is not None:
            result = ExcryptMessageResponse() if previous_response is None else previous_response

            for tag in self.response_map:
                if tag in response:
                    raw_value = response[tag]
                    destination, value = self._translate_field(raw_value, self.response_map, tag)
                    self._add_to_dict(result, destination, value)

        self.translated_response = result
        return result
