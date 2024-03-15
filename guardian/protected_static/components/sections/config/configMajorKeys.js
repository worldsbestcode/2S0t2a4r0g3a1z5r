/**
 * A component for viewing major key checksums.
 */
fxApp.component('configMajorKeys', {
    templateUrl: 'components/sections/config/configMajorKeys.html',
    controller: ['$scope', 'guardianService',
                 function ($scope, guardianService) {

        $scope.guardianService = guardianService;
        $scope.$watch('guardianService.selectedObject.objectID', function (objectID) {
            guardianService.majorKeyChecksums(guardianService.getSelectedObject(), function(checksums) {
                $scope.majorKeys = checksums;
            });
        });
    }]
});