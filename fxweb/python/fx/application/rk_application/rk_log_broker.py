"""
@file      rk_log_broker.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Does conversion and response for log download commands
"""
from broker import Broker
from rk_app_log_broker import RKAppLogBroker
from rk_audit_log_broker import RKAuditLogBroker
from rk_human_readable_config_broker import RKHumanReadableConfigBroker

LOG_BROKERS = {cls.log_category: cls for cls in [
    RKAppLogBroker,
    RKAuditLogBroker,
    RKHumanReadableConfigBroker
]}


class RKLogBroker(Broker):
    """Class For Downloading logs from the server"""

    def process(self, request_data):
        """Process client request for log
        Arguments:
            request_data: The client request data
        """
        broker = self.make_broker(request_data.get('log_category'))
        if not broker:
            return {}, 'Unknown log category'

        return broker.process(request_data)

    def make_broker(self, log_category):
        """Create a log broker object
        Arguments:
            log_category: The log broker type
        Returns: A new log broker or None if not found
        """
        log_cls = LOG_BROKERS.get(log_category)
        if log_cls:
            return log_cls(self.interface, self.context, self.user)

        return None
