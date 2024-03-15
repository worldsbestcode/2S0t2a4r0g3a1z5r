/**
 * Constructor for the Guardian sidebar controller.
 * @param {object} $scope
 * @returns {object} A new controller.
 */
var guardianController = fxApp.controller('guardianController',
['$scope', 'guardianService', 'fxAppService', function($scope, guardianService, fxAppService) {

    $scope.guardianService = guardianService;

    $scope.$watch('guardianService.getSelectionName()', function (name) {

        var contextString = '';
        if (name) {
            contextString = "Logging in to ";
            if (guardianService.isSelectionGroup()) {
                contextString += "the " + name + " group.";
            } else {
                contextString += "device at " + name + ".";
            }
        }

        guardianService.loginContextString = contextString;

        if (fxAppService.getView() === 'configView') {
            fxAppService.setRightSidebarShown(true);
        }
    });
}]);
