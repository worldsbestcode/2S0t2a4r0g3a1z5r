/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017
 * @brief The configuration view component
 */
/**
 * The base submitter view
 */
fxApp.component('configView', {
    templateUrl: 'components/sections/config/content.html'
});

fxApp.component('configReport', {
    templateUrl: 'components/sections/config/configReport.html',
    controller: ['$scope', '$interval', '$timeout', 'configReportService', 'fxProgressService',
                function ($scope, $interval, $timeout, configReportService, fxProgressService) {

        $scope.displayStates = configReportService.reportDisplayStates();
        $scope.configReportService = configReportService;
        $scope.reportFile = 'audit-log-report.txt';
        $scope.progress = fxProgressService.makeProgress();

        // Holds the interval object for the report checker
        var reportChecker = null;

        /**
         * Updates the report checker if we are not longer waiting
         */
        function updateReportChecker() {
            if (!configReportService.isWaiting() && reportChecker !== null) {
                $interval.cancel(reportChecker);
                reportChecker = null;
            }
        }

        /**
         * Does report checking in a loop in the background
         */
        function checkReport() {
            if (reportChecker === null) {
                return;
            }

            configReportService.checkReportStatus().finally(updateReportChecker);
        }



        /**
         * Called to update the progress on the screen
         */
        function finishReportProgress (reportDoneCallback) {
            fxProgressService.updateProgress($scope.progress, $scope.progress.maxProgress);
            $timeout(reportDoneCallback, 1000);
        }

        /**
         * Generate the report
         */
        $scope.generate = function () {
            var progressDelay = 500;
            var logsPerDelay = 5000;
            fxProgressService.updateProgress($scope.progress, $scope.progress.minProgress);
            configReportService.generateReport(finishReportProgress).then(function (logCount) {
                var increment = fxProgressService.incrementSize($scope.progress.maxProgress, logsPerDelay, logCount);
                fxProgressService.timedUpdate($scope.progress, progressDelay, increment, $scope.progress.maxProgress);

                // Start the report checking
                reportChecker = $interval(checkReport, 2500);
            });
        };

        // The wait button does nothing
        $scope.wait = null;
    }]
});
