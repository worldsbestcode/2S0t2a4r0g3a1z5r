"""
@author Daniel Jones (djones@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Get monitored ports from the server
"""
from broker import Broker

class RKMonitoredPortsBroker(Broker):
    """Class For Downloading logs from the server"""

    def process(self, request_data):
        """Process client request for monitored ports
        Arguments:
            request_data: The client request data
        """

        frontend_response = self.interface.get_monitored_ports()
        error = ''

        return frontend_response, error
