/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017
 * @brief Job for report function
 */

/**
 * The report service functions manage the state machine for report generation
 * @param {object}  $q  The promise interface
 * @param {object}  filterService  Provides filter schema
 * @param {object}  fxModalService  The service we use to show errors
 * @param {object}  fxAppFilterService  The filter modal
 * @param {object}  logFetchService  The service to communicate with the middleware for report generation
 * @return {object}  A set of functions for report manipulation
 */
fxApp.factory('configReportService',
    ['$q', 'filterService', 'fxAppModalService', 'fxAppFilterService', 'logFetchService',
    function ($q, filterService, fxAppModalService, fxAppFilterService, logFetchService) {

    // The report generation status
    var reportState = 'generate';

    // The filter for audit logs
    var logFilter = {};

    // The progress object to update
    var reportFinishCallback = null;

    /**
     * Return the default report state
     */
    function defaultState() {
        return 'generate';
    }

    /**
     * Create a report job information holder
     * @param {string}  jobID The jobID as a string
     */
    function createReportJob(jobID) {
        return {id: jobID, attempts: 0};
    }

    /**
     * A default job object
     */
    function defaultJob() {
        return createReportJob('0');
    }

    // The internal report object
    var reportJob = defaultJob();

    /**
     * Returns a list of displayable values for the states
     * @return {object}  A mapping from state to display value
     */
    function displayStates () {
        return {
            generate: 'Generate Report',
            wait: 'Report Generation in Progress',
            download: 'Download Report'
        };
    }

    /**
     * Check if we are waiting
     * @return {boolean}  True if waiting
     */
    function isWaiting() {
        return reportState === 'wait';
    }

    /**
     * Check if there is a report we can download
     */
    function canDownload() {
        return reportState === 'download';
    }

    /**
     * Create an error state for the report
     * @param {string}  defaultError  The error string if none is given
     * @return {function}  A function to set error state of the report
     */
    function reportFailureStatus(defaultError) {
        return function (failure) {
            reportJob = defaultJob();
            fxAppModalService.showModal('Error', failure ? failure : defaultError);
            reportState = defaultState();
            return $q.reject();
        };
    }

    /**
     * Check if the report is in the process of being generated
     * @param {string}  state  The current report state
     * @return {promise}  promise  A promise resolved if we can continue
     */
    function canCheckStatus() {
        var maxAttempts = 100;
        var deferred = $q.defer();
        if (reportJob.attempts >= maxAttempts) {
            deferred.resolve(reportFailureStatus('Report generation timed out')());
        } else {
            deferred.resolve();
        }

        return deferred.promise;
    }

    /**
     * Set the state to download
     */
    function setStateDownload() {
        reportJob = defaultJob();
        reportState = 'download';
    }

    /**
     * Check the status of a report generation
     * @param {string}  state  The current report state
     * @return {promise}  result  The result of the report status check
     */
    function checkReportStatus(state) {
        // If we aren't waiting we didn't fail but we won't check either
        if (!isWaiting()) {
            return $q.resolve();
        }

        var result = canCheckStatus(state).then(function () {
            return logFetchService.auditLogReportStatus([reportJob.id]);
        });

        result = result.then(function (statusResult) {
            var jobStatus = statusResult[reportJob.id];

            // If we can't find the job status we assume it completed and was removed
            if (!jobStatus || jobStatus === 'Complete') {
                if (reportFinishCallback) {
                    reportFinishCallback(setStateDownload);
                } else {
                    setStateDownload();
                }
            } else {
                reportJob.attempts++;
            }
        }, reportFailureStatus('Could not check report status'));

        return result;
    }

    /**
     * Generate an audit log report
     */
    function generateReport(finishCallback) {
        var filter = logFilter ? logFilter : logFetchService.auditLogFilter();

        reportFinishCallback = finishCallback;
        var result = logFetchService.auditLogGenerateReport(filter);
        return result.then(function (reportStatus) {
            reportJob = createReportJob(reportStatus.jobID);
            reportState = 'wait';
            return reportStatus.logCount;
        }, reportFailureStatus('Could not generate report'));
    }

    /**
     * Setup the filter for the report object
     */
    function setupReportFilter() {
        var useGroupConfig = true;
        fxAppFilterService.setOptions({
            clauseCondition: ['And', 'Or', 'Not'],
            criteria: {
                'Audit Log': filterService.schema.auditLog(useGroupConfig)
            }
        });

        logFilter = logFetchService.auditLogFilter();
        fxAppFilterService.setCallback(function(clauses, modalDoneCallback) {
            var filterClauses = clauses.map(function (clause) {
                return clause.values;
            });

            logFilter.request.clauses = filterService.prepareClauses(filterClauses);
            modalDoneCallback();
        });
    }

    /**
     * Display the report filter modal
     */
    function showReportFilter() {
        fxAppFilterService.showModal();
    }

    // Setup the filter modal
    setupReportFilter();

    return {
        checkReportStatus: checkReportStatus,
        generateReport: generateReport,
        isWaiting: isWaiting,
        canDownload: canDownload,
        reportDisplayStates: displayStates,
        reportFailureStatus: reportFailureStatus,
        showReportFilter: showReportFilter
    };

}]);
