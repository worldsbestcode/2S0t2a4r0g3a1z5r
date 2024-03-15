"""
@file      rk_human_readable_config_broker.py
@author    Tim Brabant (tbrabant@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Does conversion and response for human readable configuration retrieval commands.
"""

import os.path

from broker import Broker
from file_download import temp_filename, prune_download_dir
from librk import client, ManagedObjectUtils, BalancerUtils

SEND_CONFIG_CMD = client.command_str(client.eCodeConfigExport)

# Command tags for the server message
OPERATION_TAG       = 'OP'
FILENAME_TAG        = 'FN'
MANAGER_TAG         = 'MG'
OBJECT_ID_TAG       = 'ID'
RECURSIVE_TAG       = 'RO'
HTML_FORMATTING_TAG = 'HT'

class RKHumanReadableConfigBroker(Broker):
    """Class for downloading the human readable configuration log from the server."""
    log_category = 'human_readable_config'
    filename_generator = temp_filename()

    def __init__(self, interface, context, user):
        super(RKHumanReadableConfigBroker, self).__init__(interface, context, user)
        self.file_name = next(self.filename_generator)
        prune_download_dir()

    def process(self, request_data):
        """Process client request for human readable config.

        Arguments:
            request_data: The client request data.
        """
        operation = request_data.get('operation')
        if operation == 'generate':
            return self.generate_config_log(request_data)

        return {}, 'Unknown operation'

    def generate_config_log(self, request_data):
        """Generates the human readable config log file.

        Arguments:
            request_data {object} -- Request data.
        """

        error = ''
        back_response = None

        manager = request_data.get('manager')
        obj_id  = request_data.get('objectID')

        msg = self.generate_config_cmd(manager, obj_id)
        try:
            back_response = self.interface.send_dict(msg)
        except:
            return {}, "Log request timed out."

        front_response = {
            'name': 'human_readable_config',
            'operation': 'generate',
        }

        success = back_response.getField("FN")

        if success != "Y":
            error = back_response.getField("ER")

            if not error:
                error = "Unknown server error when retrieving logs."

            return {}, error
        else:
            file_name = os.path.basename(self.file_name)
            self.user.temporary_file = file_name
            front_response['filename'] = file_name

        return front_response, error

    def generate_config_cmd(self, manager, obj_id):
        """Get the config log cooking.

        Arguments:
            manager: The object manager.
            obj_id: The object ID.
        Returns: A dict with the command to send to the server.
        """
        msg = {
            'AO': SEND_CONFIG_CMD,
            FILENAME_TAG: self.file_name,
            HTML_FORMATTING_TAG: '0'
        }

        if manager is not None and obj_id is not None:
            manager_type = ManagedObjectUtils.getType(manager)
            msg[MANAGER_TAG] = str(int(manager_type))
            msg[OBJECT_ID_TAG] = obj_id

            if is_group(manager_type):
                msg[RECURSIVE_TAG] = "1"

        return msg


def is_group(manager_type):
    """Determines if a manager manages a group.

     Arguments:
        manager_type {object} -- Manager type.
    """
    return BalancerUtils.isBalancedDeviceGroup(manager_type)
