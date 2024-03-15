/**
 * A component for downloading the human readable config log.
 */
fxApp.component('configHumanReadable', {
    templateUrl: 'components/sections/config/configHumanReadable.html',
    controller: ['$scope', 'logFetchService', 'guardianService', 'fxAppModalService',
        function ($scope, logFetchService, guardianService, fxAppModalService) {

            $scope.generating = false;

            $scope.guardianService = guardianService;
            $scope.$watch('guardianService.selectedObject.objectID', function (objectID) {
                $scope.userFilename = guardianService.getSelectionName() + "-hr_config.log";
            });

            $scope.downloadHumanReadableConfig = function() {

                $scope.generating = true;
                var object = guardianService.getSelectedObject();

                var fileNameCallback = null;

                if (guardianService.isDefaultGroup(object.objectType, object.objectID)) {
                    fileNameCallback = logFetchService.humanReadableLogGenerate(null, null);
                } else {
                    fileNameCallback = logFetchService.humanReadableLogGenerate(object.objectID, object.objectType);
                }

                if (fileNameCallback) {
                    fileNameCallback.then(function(fileNameCallback) {
                        logFetchService.humanReadableLogDownload(fileNameCallback, $scope.userFilename);
                        $scope.generating = false;
                    }).catch(function (data) {
                        fxAppModalService.showModal("Error", data);
                        $scope.generating = false;
                    });
                }
            };
        }]
});