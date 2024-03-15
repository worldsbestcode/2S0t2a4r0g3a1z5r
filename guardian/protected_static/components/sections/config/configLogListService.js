/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2018
 * @brief Functions for the config log list
 */
fxApp.factory('configLogListService',
    ['$q', 'logFetchService', 'guardianService', 'fxProgressService',
    function ($q, logFetchService, guardianService, fxProgressService) {

    // The application result is cached if needed the other results could be too
    var applicationLogFiles = logFetchService.appLogList();
    var nameToLogSize = {};

    /**
     * Get the list of application logs and assigns it to the config model
     * @param {string}  objectType  The balanced object type
     * @param {string}  objectID  The balanced object id
     * @returns {promise}  A promise containing the application logs
     */
    function getLogList(objectType, objectID, parentID) {
        var fetchResult = null;
        if (guardianService.isDefaultGroupOrDevice(objectType, objectID, parentID)) {
            fetchResult = applicationLogFiles;
        } else {
            fetchResult = logFetchService.appLogList(objectType, objectID, parentID);
        }

        return fetchResult.then(function (files) {
            var logs = {};
            files.forEach(function (logFile) {
                var name = logFile.name;
                logs[name.split('/').pop()] = name;
                nameToLogSize[name] = Number.parseInt(logFile.size);
            });

            return logs;
        });
    }

    /**
     * Calculate the total download size of the given logs
     * @param {array}  logs  The logs to calculate the size for
     * @return {number}  The calculated size
     */
    function calculateDownloadSize(logs) {
        return logs.reduce(function (totalSize, logName) {
            return totalSize + nameToLogSize[logName];
        }, 0);
    }

    /**
     * Download a selected list of logs
     * @param {array}  selectedLogs  A list of filenames of the logs to download
     * @param {string}  logFilename  The filename to save the logs to
     * @param {object}  progress  The progress indicator
     */
    function downloadApplicationLogs(selectedLogs, logFilename, progress) {
        var incrementTime = 500;
        if (selectedLogs.length > 0 && logFilename) {
            var downloadSize = calculateDownloadSize(selectedLogs);
            var incrementSize = fxProgressService.downloadIncrement(progress.maxProgress, incrementTime, downloadSize);
            fxProgressService.timedUpdate(progress, incrementTime, incrementSize, progress.maxProgress);
            return logFetchService.appLogDownload(selectedLogs, logFilename);
        }

        return $q.resolve();
    }

    return {
        downloadApplicationLogs: downloadApplicationLogs,
        getLogList: getLogList
    };

}]);
