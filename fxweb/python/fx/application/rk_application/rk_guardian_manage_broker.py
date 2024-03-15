"""
@file      rk_guardian_manage_broker.py
@author    Daniel Jones (djones@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Execute guardian management commands
"""
import json
import base64
import guardian_utils
from librk import client, BalancerUtils, ManagedObjectUtils
from broker import Broker

# Command tags for the server message
DATA_TAG = 'DA'
DOMAIN_TAG = 'DM'
MANAGER_TAG = 'MN'
OBJECT_ID_TAG = 'ID'
OPERATION_TAG = 'OP'

class RKGuardianManageBroker(Broker):
    """Class For Downloading logs from the server"""
    log_category = 'application'

    def process(self, request_data):
        """Process client request for guardian management
        Arguments:
            request_data: The client request data
        """
        response = {}

        operation = request_data.get('operation')
        manager = request_data.get('manager')
        obj_id = request_data.get('objectID')
        parent_id = request_data.get('parentID')
        domain = request_data.get('domain')

        if not self.is_remote_authorized(manager, obj_id, parent_id):
            return {}, 'Not authorized for remote'

        error = ''
        if operation == 'load':
            response, error = self.load_settings(manager=manager,
                                                 obj_id=obj_id,
                                                 domain=domain)
        elif operation == 'save':
            response, error = self.save_settings(manager=manager,
                                                 obj_id=obj_id,
                                                 domain=domain,
                                                 settings=request_data.get('settings'))
        return response, error

    def load_settings(self, manager, obj_id, domain):
        """ Gets settings as json data """
        error = ''
        back_response = None

        msg = self.generate_message('load', manager, obj_id, domain)
        try:
            back_response = self.interface.send_dict(msg)
        except:
            return {}, "Guardian request timed out."

        front_response = {
            'name': 'guardian manage',
            'operation': 'load settings',
            'domain': domain,
        }

        success = back_response.getField('AN')

        if success != 'Y':
            error = back_response.getField('BB')

            if not error:
                error = 'Unknown server error'

            return {}, error
        else:
            data_str = base64.b64decode(back_response.getField('DA'))
            front_response['settings'] = json.loads(data_str)

        return front_response, error

    def save_settings(self, manager, obj_id, domain, settings):
        """ Sets settings from json data """
        error = ''
        back_response = None

        msg = self.generate_message('save', manager, obj_id, domain)
        msg[DATA_TAG] = base64.b64encode(json.dumps(settings).encode()).decode()

        try:
            back_response = self.interface.send_dict(msg)
        except:
            return {}, "Guardian request timed out."

        front_response = {
            'name': 'guardian manage',
            'operation': 'save settings',
            'domain': domain,
        }

        success = back_response.getField('AN')

        if success != 'Y':
            error = back_response.getField('BB')

            if not error:
                error = 'Unknown server error'

            return {}, error

        return front_response, error

    def generate_message(self, operation, manager, obj_id, domain):
        """ Generates a message for guardian management """
        return {
            'AO': 'RKY401',
            OPERATION_TAG: operation,
            MANAGER_TAG: manager,
            OBJECT_ID_TAG: obj_id,
            DOMAIN_TAG: domain,
        }

    def is_remote_authorized(self, manager, obj_id, parent_id):
        return guardian_utils.is_remote_object_authorized(
            manager=manager,
            obj_id=obj_id,
            parent_id=parent_id,
            user_store=self.user
        )
