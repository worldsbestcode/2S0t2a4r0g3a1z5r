"""
@author Tim Brabant (tbrabant@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2018

@section DESCRIPTION
Get major key checksums for a device.
"""

from broker import Broker


class RKMajorKeysBroker(Broker):
    """Class for delegating major key checksum requests."""

    def process(self, request_data):
        """Process client request for major key checksums.
        Arguments:
            request_data: The client request data.
        """

        frontend_response = self.interface.get_major_keys(request_data)
        error = ''

        if frontend_response.get('result') == 'Failure':
            error = frontend_response.get('message')
            frontend_response = {}

        return frontend_response, error
