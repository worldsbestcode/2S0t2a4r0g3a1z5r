/**
 * Provides functions for manipulating objects
 *
 * @returns {object} helper functions injected into view services
 */

var fxAppObjectService = fxApp.factory('fxAppObjectService',
    ['$http', '$q', 'fxAppModalService', 'fxAppDialogService',
    function($http, $q, fxAppModalService, fxAppDialogService) {

    /**
     * Adds an object on the server
     * @param {object} toAdd the new object to add
     */
    function addObject(toAdd) {
        var message = {
            "method": "create",
            "objectData": {}
        };

        message.objectData[toAdd.objectType] = [toAdd];

        $http.post(window.apipath('/object'), message).then( function(response) {
            if (response.data.result === 'Success') {
                // Do not do anything on successful add, as the GUI should update
            } else {
                fxAppModalService.showModal('Error', response.data.message);
            }
        });
    }

    /**
     * Modifies an object on the server
     * @param {object} toModify the object to modify
     */
    function modifyObject(toModify) {
        var message = {
            "objectData": {}
        };

        message.objectData[toModify.objectType] = [toModify];

        $http.put(window.apipath('/object'), message).then( function(response) {
            if (response.data.result === 'Success') {
                // Do not do anything on successful modify, as the GUI should update
            } else {
                fxAppModalService.showModal('Error', response.data.message);
            }
        });
    }

    /**
     * Deletes an object on the server
     * @param {object} toDelete the object to delete
     */
    function deleteObject(toDelete) {
        var message = {objectData: {}};
        message.objectData[toDelete.objectType] = [toDelete.objectID];

        var config = {
            "data": message,
            "headers": {'Content-Type': 'application/json'}
        };

        $http.delete(window.apipath('/object'), config).then(function (response) {
            if (response.data.result === 'Success') {
                // Do not do anything on successful delete, as the GUI should update
            } else {
                fxAppModalService.showModal('Error', response.data.message);
            }
        });
    }

    /**
     * Gets ports monitored by the server
     * @param updateCallback the callback to run after the ports are loaded from the server
     */
    function getMonitoredPorts(updateCallback) {
        var message = {
            method: "retrieve",
            name: "monitored ports",
            formData: {
                "blank": "data",
            }
        };

        return $http.post(window.apipath('/formdata'), message).then(function(response) {
            var ports = [];
            if (response.data.result === 'Success') {
                ports = response.data.formData.ports;
            } else {
                fxAppModalService.showModal('Error loading ports', response.message);
            }
            updateCallback(ports);
        });
    }
    
    /**
     * Gets major key checksums for a given object.
     *
     * @param {Object} device - Balancded device information. Optional.
     * @param {function} updateCallback - callback to run after the checksums are loaded. Optional.
     */
    function getMajorKeyChecksums(device, updateCallback) {
        var promise = window.Scaffolding.MajorKeyApi.getMajorKeyChecksums($http, device, updateCallback);

        return promise.then(function (checksums) {
          updateCallback(checksums);
        }).catch(function (error) {
          fxAppModalService.showModal('Error loading major key checksums', error);
          updateCallback({});
        });
    }

    /**
     * Starts a statistics report
     *
     * @param group the group generating the report for
     * @param the parameters of the report
     * @param continueCallback the callback to run to check if the user canceled the operation
     * @param resultsCallback the callback to run after the the report is started are loaded.
     * @param cleanupCallback the callback to run after everything completes
     */
    function generateStatisticsReport(group, params, continueCallback, resultsCallback, cleanupCallback) {
        start_message = {
            "method": "retrieve",
            "name": "statistics",
            "formData": {
                "operation": 'start',
                "statType": 'command',
                "deviceGroup": group.groupName,
                "startTime": params.startTime,
                "endTime": params.endTime,
                "command": params.command,
            }
        };

        results_message = {
            "method": "retrieve",
            "name": "statistics",
            "formData": {
                "operation": 'results',
            }
        };

        cancel_message = {
            "method": "retrieve",
            "name": "statistics",
            "formData": {
                "operation": 'cancel',
            }
        };

        var started = false;
        var stopProcessing = function (response) {
            return !continueCallback() || response.data.result !== 'Success';
        };

        // Run a poll to the server in a loop for a maximum of 10 minutes,
        // then return the result
        var pollJob = function (pollCallback, doneCallback) {
            var POLL_SLEEP = 1000;
            var TIME_OUT_MINUTES = 10;

            var deferred = $q.defer();
            var timeoutMoment = moment().add(TIME_OUT_MINUTES, 'minutes');

            var poll = function (response) {
                var todayMoment = moment();
                if (timeoutMoment < todayMoment) {
                    response.data.result = 'Timeout';
                    response.data.message = 'Server timed out';
                    deferred.resolve(response);
                } else if (doneCallback(response)) {
                    deferred.resolve(response);
                } else {
                    pollCallback().then(function (response) {
                        setTimeout(poll, POLL_SLEEP, response);
                    });
                }
            };

            pollCallback().then(poll);

            return deferred.promise;
        };

        var startedReport = false;
        return $http.post(window.apipath('/formdata'), start_message).then(function(response) {
            // Poll until user cancels or results are done
            if (stopProcessing(response)) {
                return response;
            }

            startedReport = true;

            var pollCallback = function () {
                return $http.post(window.apipath('/formdata'), results_message);
            };

            var doneCallback = function (response) {
                return stopProcessing(response) ||
                       response.data.formData.status === 'ready';
            };

            return pollJob(pollCallback, doneCallback);
        }).then(function (response) {
            // Cancel the running job if we started the report
            if (startedReport && stopProcessing(response)) {
                return $http.post(window.apipath('/formdata'), cancel_message);
            }

            return response;
        }).then(function (response) {
            // Finish getting the report
            if (continueCallback()) {
                if (response.data.result === 'Success') {
                  resultsCallback(response.data.formData.results);
                } else {
                    var error = response.data.message || 'Unknown error';
                    fxAppModalService.showModal('Error generating statistics report', error);
                }
            }
        }).finally(function () {
            cleanupCallback();
        });
    }

    /**
     * Starts a statistics report
     *
     * @param group the group generating the report for
     * @param the parameters of the report
     * @param continueCallback the callback to run to check if the user canceled the operation
     * @param resultsCallback the callback to run after the the report is started are loaded.
     * @param cleanupCallback the callback to run after everything completes
     */
    function generateStatisticsReport(group, params, continueCallback, resultsCallback, cleanupCallback) {
        start_message = {
            "method": "retrieve",
            "name": "statistics",
            "formData": {
                "operation": 'start',
                "statType": 'command',
                "deviceGroup": group.groupName,
                "startTime": params.startTime,
                "endTime": params.endTime,
                "command": params.command,
            }
        };

        results_message = {
            "method": "retrieve",
            "name": "statistics",
            "formData": {
                "operation": 'results',
            }
        };

        cancel_message = {
            "method": "retrieve",
            "name": "statistics",
            "formData": {
                "operation": 'cancel',
            }
        };

        var started = false;
        var stopProcessing = function (response) {
            return !continueCallback() || response.data.result !== 'Success';
        };

        // Run a poll to the server in a loop for a maximum of 10 minutes,
        // then return the result
        var pollJob = function (pollCallback, doneCallback) {
            var POLL_SLEEP = 1000;
            var TIME_OUT_MINUTES = 10;

            var deferred = $q.defer();
            var timeoutMoment = moment().add(TIME_OUT_MINUTES, 'minutes');

            var poll = function (response) {
                var todayMoment = moment();
                if (timeoutMoment < todayMoment) {
                    response.data.result = 'Timeout';
                    response.data.message = 'Server timed out';
                    deferred.resolve(response);
                } else if (doneCallback(response)) {
                    deferred.resolve(response);
                } else {
                    pollCallback().then(function (response) {
                        setTimeout(poll, POLL_SLEEP, response);
                    });
                }
            };

            pollCallback().then(poll);

            return deferred.promise;
        };

        var startedReport = false;
        return $http.post(window.apipath('/formdata'), start_message).then(function(response) {
            // Poll until user cancels or results are done
            if (stopProcessing(response)) {
                return response;
            }

            startedReport = true;

            var pollCallback = function () {
                return $http.post(window.apipath('/formdata'), results_message);
            };

            var doneCallback = function (response) {
                return stopProcessing(response) ||
                       response.data.formData.status === 'ready';
            };

            return pollJob(pollCallback, doneCallback);
        }).then(function (response) {
            // Cancel the running job if we started the report
            if (startedReport && stopProcessing(response)) {
                return $http.post(window.apipath('/formdata'), cancel_message);
            }

            return response;
        }).then(function (response) {
            // Finish getting the report
            if (continueCallback()) {
                if (response.data.result === 'Success') {
                  resultsCallback(response.data.formData.results);
                } else {
                    var error = response.data.message || 'Unknown error';
                    fxAppModalService.showModal('Error generating statistics report', error);
                }
            }
        }).finally(function () {
            cleanupCallback();
        });
    }

	return {
        addObject: addObject,
        modifyObject: modifyObject,
        deleteObject: deleteObject,
        getMonitoredPorts: getMonitoredPorts,
        getMajorKeyChecksums: getMajorKeyChecksums,
        generateStatisticsReport: generateStatisticsReport,
   };
}]);

