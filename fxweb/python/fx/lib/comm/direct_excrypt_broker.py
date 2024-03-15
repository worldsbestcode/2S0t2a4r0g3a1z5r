"""
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, L.P. 2018
"""

from abc import abstractmethod
from broker import Broker

class DirectExcryptBroker(Broker):
    """Broker for converting frontend requests to backend excrypt requests"""

    def process(self, request_data):
        """Process a frontend request

        Args:
            request_data: The frontend request json

        Returns:
            Tuple of the response to the frontend and any error
        """
        field_tags = self.generate_message(request_data)
        backend_response = self.interface.send_dict(field_tags)

        frontend_response = {}
        error = ''

        if not backend_response:
            error = 'Backend request timed out'
        elif self.is_error(backend_response):
            error = self.parse_error(backend_response)
            if not error:
                error = 'Error processing backend request'
        else:
            frontend_response = self.parse_response(backend_response)

        return frontend_response, error

    def is_error(self, backend_response):
        """Determines if the backend response is an error

        Args:
            backend_response: The backend response (an excrypt message)

        Returns:
            Whether or not the given message is an error message
        """
        error = backend_response.getField('AO') == 'ERRO'

        if not error:
            error = backend_response.getField('AN') in ('N', 'P')

        return error

    def parse_error(self, backend_response):
        """Creates an error string from the backend response

        Args:
            backend_response: The backend response (an excrypt message)

        Returns:
            An error string
        """
        error = backend_response.getField('BB')

        if not error and backend_response.getField('AN') == 'P':
            error = 'Permissions lacking'

        if not error and backend_response.getField('AN') == 'N':
            error = 'General failure'

        if not error:
            error = 'Internal error'

        return error

    @abstractmethod
    def parse_response(self, backend_response):
        """Converts the backend response into a frontend response

        Args:
            backend_response: The backend response

        Returns:
            A map of responses to be jsonified and sent back to the frontend
        """
        pass

    @abstractmethod
    def generate_message(self, frontend_request):
        """Converts the backend response into a frontend response

        Args:
            backend_response: The backend response

        Returns:
            A map of excrypt tag:value pairs
        """
        pass
