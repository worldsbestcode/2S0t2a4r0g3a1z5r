"""
@file      rk_formdata.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
View for remote key formdata
"""
from flask import jsonify, request
from auth import login_required

from app_csrf import csrf_required
from app_sanitize import sanitize_request
from rk_log_broker import RKLogBroker
from rk_monitored_ports_broker import RKMonitoredPortsBroker
from rk_major_keys_broker import RKMajorKeysBroker
from rk_guardian_manage_broker import RKGuardianManageBroker
from rk_statistics_broker import RKStatisticsBroker
from server_views import ServerDefaultView

# The brokers mediate for non-object commands
RK_FORM_BROKERS = {
    'guardian manage': RKGuardianManageBroker,
    'logs': RKLogBroker,
    'major keys': RKMajorKeysBroker,
    'monitored ports': RKMonitoredPortsBroker,
    'statistics': RKStatisticsBroker,
}


class RKFormDataView(ServerDefaultView):
    """Remotekey view for /formdata"""
    decorators = [sanitize_request, csrf_required]

    def __init__(self, server_interface, brokers=RK_FORM_BROKERS):
        """Initialize the form data view"""
        super(RKFormDataView, self).__init__(server_interface)
        self.brokers = brokers

    def post(self, *args, **kwargs):
        """Process form data requests"""
        post_data = request.get_json()
        name = post_data.get('name')
        broker_cls = self.brokers.get(name)
        form_data = post_data.get('formData')
        error = ''
        if not name:
            error = 'No field "name" received'
        elif not form_data:
            error = 'No field "formData" received'
        elif not broker_cls:
            error = 'Could not match "{}" to formData type'.format(name)

        if error:
            return jsonify(result='Failure', message=error, objectData={})

        frontend_response = {}
        if post_data.get('method') == 'retrieve' and broker_cls:
            context = self._get_current_user().context
            broker = broker_cls(self.server_interface, context,
                                self._get_current_user())
            frontend_response, error = broker.process(form_data)

        if not frontend_response or error:
            return jsonify(result='Failure', message=error, objectData={})

        return jsonify(result='Success', formData=frontend_response)
