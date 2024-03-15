/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017
 * @brief Fetch audit and application log files
 */
logFetchService.$inject = ['$http', '$q', 'filterService', 'fxAppStringService'];
function logFetchService($http, $q, filterService, fxAppStringService) {

    /**
     * Return the function error
     * @param {object}  reponse  The response from the server
     * @param {string}  defaultError  The error string if the response does not contain one
     * @returns {promise}  A promise containing formData if there is no error
     */
    function checkResponse(response, defaultError) {
        if (response.data.result === 'Failure') {
            return $q.reject(response.data.message ? response.data.message : defaultError);
        }

        return $q.resolve(response.data.formData);
    }

    /**
     * Return the log request format
     * @param {string}  logCategory  The type of log
     * @param {string}  operation  The type of operation
     * @param {object}  additionalFields  Any other fields to add (optional)
     * @return {object}  A log formdata request
     */
    function logRequest(logCategory, operation, additionalFields) {
        var request = {
            method: 'retrieve',
            name: 'logs',
            formData: {
                log_category: logCategory,
                operation: operation
            }
        };

        for (var key in additionalFields) {
            request.formData[key] = additionalFields[key];
        }

        return request;
    }

    /**
     * Generate the human readable config log request object.
     *
     * @param {any} objectID ID of the object to get the log for.
     * @param {any} manager Manager of the object to get the log for.
     * @returns {object} Log request object.
     */
    function humanReadableLogGenerateRequest(objectID, manager) {
        var objectFields;
        if (manager && objectID) {
            objectFields = {manager: manager, objectID: objectID};
        }

        return logRequest('human_readable_config', 'generate', objectFields);
    }

    /**
     * Generate the human readable config log.
     *
     * @param {any} objectID ID of the object to get the log for.
     * @param {any} manager Manager of the object to get the log for.
     * @returns {promise}  A promise containing the file name of the generated file.
     */
    function humanReadableLogGenerate(objectID, manager) {
        var listRequest = humanReadableLogGenerateRequest(objectID, manager);
        return $http.post(window.apipath('/formdata'), listRequest).then(humanReadableLogGenerateProcess);
    }

    /**
     * Process the human readable log response and return the file name.
     * @param {object}  response  The server response.
     * @return {string}  file_name  The file name.
     */
    function humanReadableLogGenerateProcess(response) {
        var result = checkResponse(response, 'Unexpected human readable config log list processing error');
        return result.then(function(formData) {
            return formData.filename;
        });
    }

    /**
     * Download the given human readable config file.
     * @param {string}  filename  The file to download.
     * @param {string}  userFilename  The name of the file to download them to.
     */
    function humanReadableLogDownload(filename, userFilename) {
        return $http.get(window.apipath('/download/' + filename),
            { transformResponse: [
                function(data) {
                    return data;
            }]
        }).then(function(response) {
            return fxAppStringService.downloadString(response.data, userFilename);
        });
    }

    /**
     * Return a list of all the app log files
     * @param {string}  manager  The balanced object manager (optional)
     * @param {string}  objectID  The object's ID (optional)
     * @return {object}  A request object
     */
    function appLogListRequest(manager, objectID, parentID) {
        var objectFields;
        if (manager && objectID) {
            objectFields = {manager: manager, objectID: objectID, parentID: parentID};
        }

        return logRequest('application', 'list', objectFields);
    }

    /**
     * Process the app log list response and return the file list
     * @param {object}  response  The server response
     * @return {array}  file_list  The file list array
     */
    function appLogListProcess(response) {
        var result = checkResponse(response, 'Unexpected application log list process error');
        return result.then(function(formData) {
            return formData.file_list;
        });
    }

    /**
     * Query for the application log list and return a response
     * @param {string}  manager  The balanced object manager (optional)
     * @param {string}  objectID  The object's ID (optional)
     * @returns {promise}  A promise containing the file list response
     */
    function appLogList(manager, objectID, parentID) {
        var listRequest = appLogListRequest(manager, objectID, parentID);
        return $http.post(window.apipath('/formdata'), listRequest).then(appLogListProcess);
    }

    /**
     * Download app log files
     * @param {array}  files  A list of files to return
     */
    function appLogDownloadRequest(files) {
        return logRequest('application', 'download', {file_list: files});
    }

    /**
     * Process the download data from the server
     * @param {object}  response  The middleware response
     * @param {string}  filename  The storage location of the file
     * @return {promise}  A promise containing nothing
     */
    function appLogDownloadProcess(response, filename) {
        var result = checkResponse(response, 'Could not download application log');
        return result.then(function (formData) {
            fxAppStringService.downloadBase64String(formData.log_data, filename);
        });
    }

    /**
     * Download the given file list
     * @param {array}  files  The list of files to download
     * @param {string}  filename  The name of the file to download them to
     */
    function appLogDownload(files, filename) {
        return $http.post(window.apipath('/formdata'), appLogDownloadRequest(files)).then(function(response) {
            return appLogDownloadProcess(response, filename);
        });
    }

    /**
     * Creates an empty audit log filter
     * @return {object}  An empty audit log filter
     */
    function auditLogFilter() {
        var ordering = filterService.orderingData(0);
        var request = filterService.requestData('LOG');
        return filterService.makeFilter(request, ordering);
    }

    /**
     * Create the request method for the audit log report
     * @param {object}  logFilter  The filter object to query
     * @return {object}  A report generation query
     */
    function auditLogGenerateRequest(logFilter) {
        return logRequest('audit', 'generate', {filter: logFilter});
    }

    /**
     * Process the response from the audit log generate
     */
    function auditLogGenerateProcess(response) {
        var result = checkResponse(response, 'Could not generate log report');

        /**
         * Translate the response into a filename/jobID combo
         * @param {object}  formData  The data to translate
         * @return {object}  An object with fileName and jobID fields
         */
        function processResponseInternal(formData) {
            return {
                fileName: formData.report,
                jobID: formData.job_id,
                logCount: formData.count
            };
        }

        return result.then(processResponseInternal);
    }

    /**
     * Generate the audit log report from the given filter
     *
     */
    function auditLogGenerate(logFilter) {
        return $http.post(window.apipath('/formdata'), auditLogGenerateRequest(logFilter)).then(auditLogGenerateProcess);
    }

    /**
     * Check on the status of an audit log export
     * @param {array}  jobIDs  The list of ids
     * @return {object}  A server status request
     */
    function auditLogStatusRequest(jobIDs) {
        return logRequest('audit', 'status', {ids: jobIDs});
    }

    /**
     * Process the audit log status response
     * @param {object}  data  Response from the audit log
     */
    function auditLogStatusProcess(response) {
        return checkResponse(response, 'Could not get job status');
    }

    /**
     * Query the server for job status
     * @param {array}  jobIDs  The list of job ids to check for
     */
    function auditLogStatus(jobIDs) {
        return $http.post(window.apipath('/formdata'), auditLogStatusRequest(jobIDs)).then(auditLogStatusProcess);
    }

    return {
        appLogList: appLogList,
        appLogDownload: appLogDownload,
        auditLogFilter: auditLogFilter,
        auditLogGenerateReport: auditLogGenerate,
        auditLogReportStatus: auditLogStatus,
        checkResponse: checkResponse,
        humanReadableLogDownload: humanReadableLogDownload,
        humanReadableLogGenerate: humanReadableLogGenerate
    };
}

fxApp.factory('logFetchService', logFetchService);
