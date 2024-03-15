fxApp.directive('fxSpinner', [function () {
    return {
        templateUrl: 'directives/fxSpinner.html',
        restrict: 'E',
        scope: {
            name: '@'
        },
        controller : ['$scope', 'fxSpinnerService', function($scope, fxSpinnerService) {
                $scope.show = true;

                var spinner = {
                    name: $scope.name,
                    show: function() {
                        $scope.show = true;
                    },
                    remove: function() {
                        $scope.show = false;
                    },
                };

                fxSpinnerService.register(spinner);
        }]
        };
    }
]);

