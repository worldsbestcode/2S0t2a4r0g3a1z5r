/**
 * A component for selecting logs to download
 */
fxApp.component('configLogList', {
    templateUrl: 'components/sections/config/configLogList.html',
    controller: ['$scope', '$timeout', 'configLogListService', 'guardianService', 'fxProgressService',
                 function ($scope, $timeout, configLogListService, guardianService, fxProgressService) {

        $scope.logs = {};

        // The application logs use a path to name format used by the selection component
        $scope.applicationLogs = {};

        $scope.container = {
            selected: []
        };

        $scope.isLoading = false;
        $scope.logFilename = '';
        $scope.progress = fxProgressService.makeProgress();
        $scope.devicesMissingSyslog = "";

        // Async version of log download
        var asyncLogDownload = async.asyncify(configLogListService.downloadApplicationLogs);

        /**
         * Update application logs using the new logs
         */
        function updateAppLogs(logs) {
            $scope.logs = logs;
            var pathToName = {};
            Object.keys(logs).forEach(function (filename) {
                pathToName[logs[filename]] = filename;
            });

            $scope.applicationLogs = pathToName;
        }

        /**
         * Update the application logs
         * @param {string}  objectType  The selected object type
         * @param {string}  objectID  The selected object id
         * @param {string}  parentID  The selected object parent id
         */
        function reloadAppLogs(objectType, objectID, parentID) {
            configLogListService.getLogList(objectType, objectID, parentID).then(updateAppLogs);
        }

        /**
         * Update devices that do not have syslog forwarding
         * @param selectedObject the object that is selected by guardian service
         */
        function checkSyslogForwarding(selectedObject) {
            var devices = [];
            if (guardianService.isGroupType(selectedObject.objectType)) {
                devices = selectedObject.children;
            } else {
                devices = [selectedObject];
            }

            var noSyslogDevices = devices.filter(function (device) {
                return !device.receiveSyslog;
            });

            var noSyslogAddresses = noSyslogDevices.map(function (device) {
                return device.deviceAddress;
            });

            $scope.devicesMissingSyslog = noSyslogAddresses.join();
        }

        // Instantiate the app logs
        reloadAppLogs(guardianService.selectedObject.objectType,
                      guardianService.selectedObject.objectID,
                      guardianService.selectedObject.parentID);

        $scope.guardianService = guardianService;
        $scope.$watch('guardianService.selectedObject.objectID', function (objectID) {
            $scope.container.selected = [];
            reloadAppLogs(guardianService.selectedObject.objectType, objectID, guardianService.selectedObject.parentID);
            checkSyslogForwarding(guardianService.selectedObject.object);
        });

        /**
         * Given a the current list and the previous list assign the download filename
         * @param {array}  selectedLogs  The current list of logs to use for creating a placeholder name
         * @param {array}  previous  The previously list of logs (optional)
         */
        function updateFilename(selectedLogs, previous) {
            var currentLength = selectedLogs.length;
            var previousLength = previous ? previous.length : 0;

            var newLogFilename = $scope.logFilename;
            if (currentLength === 0) {
                newLogFilename = '';
            } else if (currentLength === 1) {
                newLogFilename = selectedLogs[0];
            } else if (currentLength > 1 && previousLength <= 1) {
                newLogFilename = 'log-archive.tar.gz';
            }

            return newLogFilename;
        }

        $scope.$watchCollection('container.selected', function(newSelected, oldSelected) {
            $scope.logFilename = updateFilename(newSelected, oldSelected);
        });

        /**
         * Function for downloading a given list of logs
         * @param {array}  downloadLogs  A list of log display names to download
         * @param {string}  downloadFilename  The name of the downloaded file
         */
        function downloadSelectedLogs(downloadLogs, downloadFilename) {
            if (downloadLogs.length === 0) {
                return;
            }

            // If the filename is empty just use the default
            if (!downloadFilename) {
                downloadFilename = updateFilename(downloadLogs);
            }

            // Translate the log names to paths
            var logPaths = downloadLogs.map(function (filename) {
                return $scope.logs[filename];
            });

            fxProgressService.updateProgress($scope.progress, $scope.progress.minProgress);
            $scope.isLoading = true;

            asyncLogDownload(logPaths, downloadFilename, $scope.progress, function (error, result) {
                fxProgressService.updateProgress($scope.progress, $scope.progress.maxProgress);
                $timeout(function () {
                    $scope.isLoading = false;
                }, 1000);
            });
        }

        /**
         * Function for downloading the list of selected logs
         */
        $scope.downloadSelected = function () {
            downloadSelectedLogs($scope.container.selected, $scope.logFilename);
        };

        /**
         * Download all application logs
         */
        $scope.downloadAll = function () {
            var downloadLogs = Object.keys($scope.logs);
            var downloadFilename = $scope.logFilename;
            if ($scope.container.selected.length === 1 && downloadFilename === $scope.container.selected[0]) {
                downloadFilename = updateFilename(downloadLogs);
            }

            downloadSelectedLogs(downloadLogs, downloadFilename);
        };
    }]
});
