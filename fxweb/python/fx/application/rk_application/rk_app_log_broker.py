"""
@file      rk_app_log_broker.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Does conversion and response for log download commands
"""
import base64
import os.path
import tempfile
import tarfile
import guardian_utils
from collections import namedtuple
from librk import client, BalancerUtils, ManagedObjectUtils

from broker import Broker
from application_log import ApplicationLogger as Log

SEND_LOG_CMD = client.command_str(client.eCodeSendServerLogs)

ALLOWED_LOG_DIRS = [
    '/rkdata',
    '/rkdata/devices',
    '/var/log',
    '/var/log/postgresql',
]

# Command tags for the server message
OPERATION_TAG = 'OP'
FILENAME_TAG = 'FN'
MANAGER_TAG = 'MN'
OBJECT_ID_TAG = 'ID'

# Operation for the command
OP_DOWNLOAD = 'DL'
OP_LIST = 'LS'
OP_VERIFY = 'VR'

LOG_LIST_RESPONSE = {
    'LS': 'file_list',
    'BB': 'status',
    'AK': 'error'
}

LogListResponse = namedtuple('LogListResponse', LOG_LIST_RESPONSE.values())


def normalize_file_list(file_list):
    """Remove invalid paths and re-add the '/rkdata'
    Arguments:
        file_list: A list of files to normalize
    Returns:
        A list of normalized files
    """
    ret_list = []
    for file_path in file_list:
        normalized_path = file_path
        expanded_path = os.path.realpath(normalized_path)
        directory = os.path.dirname(expanded_path)
        if expanded_path == normalized_path and os.path.isfile(expanded_path):
            if directory in ALLOWED_LOG_DIRS:
                ret_list.append(expanded_path)

    return ret_list


def log_field_parse(field_data):
    """Parses the data sent from the server
    Arguments:
        field_data: The log list response from the server
    """
    def single_log_parse(log_data):
        """Parses a single log response
        Arguments:
            log_data: A string with filename and size
        Returns: A name and size mapping for the log
        """
        name, size = log_data.split(':')
        return {
            'name': name,
            'size': size
        }

    data = [entry for entry in field_data.split(',') if ':' in entry]
    return [single_log_parse(entry) for entry in data]


class RKAppLogBroker(Broker):
    """Class For Downloading logs from the server"""
    log_category = 'application'

    def process(self, request_data):
        """Process client request for log download
        Arguments:
            request_data: The client request data
        """
        response = {}
        operation = request_data.get('operation')
        if operation == 'list':
            response, error = self.get_log_list(manager=request_data.get('manager'),
                                         obj_id=request_data.get('objectID'),
                                         parent=request_data.get('parentID'))
        elif operation == 'download':
            response, error = self.download_log(request_data.get('file_list'))

        return response, error

    def convert_list_response(self, message):
        """Convert the list response to an object
         Arguments:
             message: The message to convert
         Returns: A tuple of the message
         """
        return self.interface.convert_message(message, LOG_LIST_RESPONSE,
                                              LogListResponse)

    @staticmethod
    def filter_device_logs(logs):
        """Filter all devices from the list
        Arguments:
            logs: A list of log entries
        Returns: A tuple of the message
        """
        return [log for log in logs if '/devices/' not in log['name']]

    @staticmethod
    def log_list_cmd(manager, obj_id):
        """Get the log list command
        Arguments:
            manager: The object manager
            obj_id: The object id
        Returns: A dict with the command to send to the server
        """
        msg = {'AO': SEND_LOG_CMD, OPERATION_TAG: OP_LIST}
        if manager is not None and obj_id is not None:
            msg[MANAGER_TAG] = manager
            msg[OBJECT_ID_TAG] = obj_id

        return msg

    @staticmethod
    def log_verify_cmd(file_list):
        """Get the log list command
        Arguments:
            file_list: Log names to verify permissions over
        Returns: A dict with the command to send to the server
        """

        csv_list = ','.join(file_list)
        msg = {
            'AO': SEND_LOG_CMD,
            OPERATION_TAG: OP_VERIFY,
            FILENAME_TAG: csv_list,
        }

        return msg

    def is_remote_authorized(self, manager, obj_id, parent_id):
        return guardian_utils.is_remote_object_authorized(
            manager=manager,
            obj_id=obj_id,
            parent_id=parent_id,
            user_store=self.user
        )

    def get_log_list(self, manager=None, obj_id=None, parent=None):
        """Get A list of log files
        Returns: A response containing a list of log files or an error
        """
        if not self.is_remote_authorized(manager, obj_id, parent):
            return {}, 'Not authorized for remote'

        msg = self.log_list_cmd(manager, obj_id)
        back_response = self.interface.send_dict(msg)
        if back_response:
            back_response = self.convert_list_response(back_response)

        front_response = {
            'name': 'server_logs',
            'operation': 'list',
        }

        error = ''
        if not back_response:
            error = 'No response from server'
        elif back_response.error:
            error = back_response.error
        elif back_response.status == 'N':
            error = 'Server did not process request'
        elif back_response.file_list:
            logs = log_field_parse(back_response.file_list)
            # If we didn't query for device logs remove them
            if manager is None or obj_id is None:
                logs = self.filter_device_logs(logs)

            front_response['file_list'] = logs
        else:
            error = 'Unknown command error'

        return front_response, error

    def verify_file_list(self, file_list):
        """Get A list of log files
            file_list: the list of log file names to verify permisisons over
        Returns: Any errors that occured
        """
        msg = self.log_verify_cmd(file_list)
        back_response = self.interface.send_dict(msg)

        error = ''
        if not back_response:
            error = 'No response from server'
        elif back_response.getField('BB') != 'Y':
            error = 'Permission denied'

        return error

    def download_request(self, files):
        """Creates the download request
        Arguments:
            files: The file to download
        Returns:
            A dictionary containing the download request
        """
        return {
            'AO': SEND_LOG_CMD,
            OPERATION_TAG: OP_DOWNLOAD,
            FILENAME_TAG: files
        }

    def download_log(self, file_list):
        """Does log download operation
        Arguments:
            file_list: A list of log file names
        Returns:
            Front response containing the log file or an error
        """
        front_response = {
            'name': 'server_logs',
            'operation': 'download'
        }

        if file_list:
            file_list = normalize_file_list(file_list)

        error = self.verify_file_list(file_list)
        if error:
            pass
        elif file_list is None:
            error = 'No file list received'
        elif not file_list:
            error = 'Empty file list received'
        elif len(file_list) == 1:
            self.download_single(file_list[0], front_response)
        else:
            self.download_multiple(file_list, front_response)

        return front_response, error

    def download_single(self, file_path, front_response):
        """Does download for a single log file
        Arguments:
            file_path: The log file path
            front_response: Place to store log data response
        """
        front_response['log_data'] = ''
        with open(file_path, 'rb') as log_file:
            front_response['log_data'] = base64.b64encode(log_file.read()).decode()

    def download_multiple(self, files, front_response):
        """Download multiple log files
        Arguments:
            files: The list of log files to download
            front_response: The client response where we store the log data
        """
        front_response['log_data'] = ''
        Log.info('Creating multi log archive for {} logs'.format(len(files)))
        with tempfile.TemporaryFile() as temp:
            with tarfile.open(mode='w:gz', fileobj=temp) as archive:
                Log.info('Adding {} log file(s) to archive'.format(len(files)))
                for file_path in files:
                    try:
                        archive.add(file_path)
                    except IOError as error:
                        Log.error('Could not add file {} to archive: {}'
                                  .format(file_path, error))
                archive.close()

            temp.seek(0)
            archive_data = temp.read()
            front_response['log_data'] = base64.b64encode(archive_data).decode()
