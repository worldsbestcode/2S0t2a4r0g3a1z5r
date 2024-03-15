"""
@file      rk_statistics_broker.py
@author    Daniel Jones (djones@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2019

@section DESCRIPTION
Execute statistics report commands
"""
import json
import base64
import guardian_utils
from librk import client, BalancerUtils, ManagedObjectUtils
from broker import Broker

# Request tags
OPERATION_TAG = 'CM'
STAT_TYPE_TAG = 'TI'
START_TIME_TAG = 'FS'
END_TIME_TAG = 'FE'
DEVICE_GROUP_TAG = 'DG'
COMMAND_TAG = 'CO'

# Response tags
SUCCESS_TAG = 'AN'
ERROR_MSG_TAG = 'BB'
STATUS_TAG = 'RS'
RESULTS_TAG = 'RP'

class RKStatisticsBroker(Broker):
    """Class For generating statistics reports"""

    def process(self, request_data):
        """Process client request for statistics report
        Arguments:
            request_data: The client request data
        """
        response = {}

        operation = request_data.get('operation')
        stat_type = request_data.get('statType')
        device_group = request_data.get('deviceGroup')
        start_time = request_data.get('startTime')
        end_time = request_data.get('endTime')
        command = request_data.get('command')

        error = ''
        if operation == 'start':
            response, error = self._start_report(stat_type=stat_type,
                device_group=device_group,
                start_time=start_time,
                end_time=end_time,
                command=command)
        elif operation == 'cancel':
            response, error = self._cancel_report()
        elif operation == 'results':
            response, error = self._get_results()

        return response, error


    def _start_report(self, stat_type, device_group, start_time, end_time, command):
        """ Starts a statistics report """
        error = ''
        back_response = None

        # Cancel any running reports
        msg = self._generate_message('CANCEL')
        try:
            back_response = self.interface.send_dict(msg)
        except:
            return {}, "Statistics cancel previous report timed out."

        msg = self._generate_message('START')
        msg[STAT_TYPE_TAG] = stat_type.upper()
        msg[DEVICE_GROUP_TAG] = device_group
        msg[START_TIME_TAG] = start_time
        msg[END_TIME_TAG] = end_time
        if command.lower() != 'any':
            msg[COMMAND_TAG] = command

        try:
            back_response = self.interface.send_dict(msg)
        except:
            return {}, "Statistics start report timed out."

        front_response = {
            'name': 'statistics',
            'operation': 'start report',
        }

        success = back_response.getField('AN')

        if success != 'Y':
            error = back_response.getField(ERROR_MSG_TAG)

            if not error:
                error = 'Unknown server error'

            return {}, error

        return front_response, error


    def _cancel_report(self):
        """ Cancels any running statistics report (under the current user) """
        error = ''
        back_response = None

        msg = self._generate_message('CANCEL')

        try:
            back_response = self.interface.send_dict(msg)
        except:
            return {}, "Statistics cancel report timed out."

        front_response = {
            'name': 'statistics',
            'operation': 'cancel report',
        }

        success = back_response.getField(SUCCESS_TAG)

        if success != 'Y':
            error = back_response.getField(ERROR_MSG_TAG)

            if not error:
                error = 'Unknown server error'

            return {}, error

        return front_response, error


    def _get_results(self):
        """
        Gets the results of a statistcs report, will return status of "not ready"
        if the results are still procesing on the server
        """
        error = ''
        back_response = None

        msg = self._generate_message('RESULTS')

        try:
            back_response = self.interface.send_dict(msg)
        except:
            return {}, "Statistics results request timed out."

        status = back_response.getField(STATUS_TAG)
        results = back_response.getField(RESULTS_TAG)

        front_response = {
            'name': 'statistics',
            'operation': 'get results',
            'status': status.lower(),
            'results': results,
        }

        success = back_response.getField(SUCCESS_TAG)

        if success != 'Y':
            error = back_response.getField(ERROR_MSG_TAG)

            if not error:
                error = 'Unknown server error'

            return {}, error

        return front_response, error


    def _generate_message(self, operation):
        """ Generates a message for statistics reports"""
        return {
            'AO': client.command_str(client.eCodeStatReport),
            OPERATION_TAG: operation,
        }
