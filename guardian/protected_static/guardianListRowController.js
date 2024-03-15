fxApp.controller('guardianListRowController', ['guardianService', '$scope',
    function(guardianService, $scope) {
        $scope.setColor = function(columnName) {
            var color = '';
            if (columnName === 'groupState' || columnName === 'deviceStatus') {
                color = guardianService.getStateClass($scope.rowObject[columnName]);
            }
            return color;
        };
    }
]);
