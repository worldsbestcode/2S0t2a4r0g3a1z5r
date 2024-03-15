/**
 * A component for downloading the command report log.
 */
fxApp.component('configCommandReport', {
  templateUrl: 'components/sections/config/configCommandReport.html',
  controller: ['$scope', '$q', 'guardianService', 'nodeViewService', 'fxAppModalService', 'filterService', 'fxAppObjectService',
    function ($scope, $q, guardianService, nodeViewService, fxAppModalService, filterService, fxAppObjectService) {

      var stopDownload = function () {
          $scope.generating = false;
      };

      var startDownload = function () {
          $scope.generating = true;
      };

      stopDownload();

      $scope.selectedDate = {
          'begin': moment().add(-1, 'month').startOf('month').toDate(),
          'end': moment().add(-1, 'month').endOf('month').toDate(),
      };
      $scope.userFilename = "command_report.csv";

      $scope.cancelDownload = function () {
          stopDownload();
      }

      $scope.downloadCommandReport = function() {
          // Don't download twice
          if ($scope.generating) {
              return;
          }

          startDownload();

          var period = $scope.selectedDate;
          var groupName = guardianService.getSelectedObject().groupName;
          var command = 'any';

          var params = {
              'startTime': period.begin.toISOString(),
              'endTime': period.end.toISOString(),
              'command': command,
          }

          var continueCallback = function () {
              return $scope.generating;
          };
          var resultsCallback = function (results) {
              Scaffolding.downloadFile(results, 'text/csv', $scope.userFilename);
          };
          var cleanupCallback = stopDownload;

          fxAppObjectService.generateStatisticsReport(guardianService.getSelectedObject(),
              params, continueCallback, resultsCallback, cleanupCallback);
      };
}]});
