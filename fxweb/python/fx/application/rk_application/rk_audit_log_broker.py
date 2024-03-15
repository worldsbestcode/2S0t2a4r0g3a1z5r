"""
@file      rk_audit_log_broker.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Does conversion and response for log download commands
"""
import os
import json
from broker import Broker
from app_matcher import QueryMatcher
from application_log import ApplicationLogger as Log
from file_download import temp_filename, prune_download_dir
from librk import (
    client,
    ExcryptMessage,
    Filter,
    MOAction,
    ManagedObject,
    ManagedObjectUtils
)

LOG_MANAGER_NAME = ManagedObjectUtils.getManagerName(ManagedObject.LOG)


class RKAuditLogBroker(Broker):
    """Class For Downloading logs from the server"""
    log_category = 'audit'
    filename_generator = temp_filename()

    def __init__(self, interface, context, user):
        super(RKAuditLogBroker, self).__init__(interface, context, user)
        self.file_name = next(self.filename_generator)
        prune_download_dir()

    def process(self, request_data):
        """Process client request for log
        Arguments:
            request_data: The client request data
        """
        operation = request_data.get('operation')
        if operation == 'generate':
            return self.generate_report(request_data)
        elif operation == 'status':
            return self.get_job_status(request_data)

        return {}, 'Unknown operation'

    def get_report_count(self, report_filter):
        """Get a count of the logs in the report
        Arguments:
            report_filter:
        Returns: The report count as a string
        """
        report_filter.setFilterType(Filter.COUNT)
        report_matcher = self.make_report_matcher()
        response = self.interface.query_rk_filter(report_filter, self.context,
                                                  matcher=report_matcher,
                                                  sync=True)[0]

        return ExcryptMessage(response).getField('MC')

    def generate_report(self, request_data):
        """Generate a filter reports
        Arguments:
            request_data: The report request used to create the filter
        """
        report_filter = Filter()
        report_filter.fromJSONString(json.dumps(request_data['filter']),
                                     MOAction.eMOActionCreate)
        report_filter.setManager(LOG_MANAGER_NAME)
        report_filter.setFile(self.file_name)

        # Get a report count before we send the request
        count = self.get_report_count(report_filter)

        report_filter.setFilterType(Filter.REPORT)
        report_filter.clearFlag(Filter.PRESERVE_SYNC_RESP)

        report_matcher = self.make_report_matcher()
        response = self.interface.query_rk_filter(report_filter, self.context,
                                                  matcher=report_matcher,
                                                  sync=False)[0]

        job_id = -1
        excrypt = ExcryptMessage(response)
        if excrypt.getFieldAsBool('BB', 'Y'):
            job_id = int(excrypt.getField('JI'))

        if job_id <= 0:
            error = 'Could not create report job'
            Log.error('Report generation failed: ' + error)
            return {}, error

        file_name = os.path.basename(self.file_name)
        self.user.temporary_file = file_name
        return dict(report=file_name, job_id=str(job_id), count=count), ''

    def get_job_status(self, request_data):
        """Return The status of a job"""
        job_filter = Filter()
        job_filter.setManager(ManagedObjectUtils.getManagerName(ManagedObject.JOB))
        id_list = [str(job_id) for job_id in request_data.get('ids')]
        job_filter.setIDs(ManagedObject.JOB, ','.join(id_list))

        responses = self.interface.query_rk_filter(job_filter,
                                                   self.context,
                                                   matcher=self.make_job_matcher(),
                                                   sync=True)

        frontend_response = {}
        filter_command = client.command_str(client.eCodeQueryFilter)

        for response in responses:
            excrypt = ExcryptMessage(response)
            if excrypt.getCommand() == filter_command:
                continue

            job = ManagedObjectUtils.createObjectFromTypeTake(ManagedObject.JOB, 0)
            job.fromMessage(excrypt)
            job_json = json.loads(job.toJSONString())
            frontend_response[job_json['objectID']] = job_json['jobStatus']

        return frontend_response, ''

    def make_report_matcher(self):
        """Create a matcher for the report job
        Returns: A new job matcher
        """
        return QueryMatcher([ManagedObject.LOG],
                            self.context.get_resp_synch_tag(),
                            self.context.inc_synch_value())

    def make_job_matcher(self):
        """Create a matcher for the report job
        Returns: A new job matcher
        """
        return QueryMatcher([ManagedObject.JOB],
                            self.context.get_resp_synch_tag(),
                            self.context.inc_synch_value())
