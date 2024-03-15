/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2018
 * @brief Implements rolling statistics for the node view
 */
fxApp.component('nodeStatBox', {
    bindings: {
        'statType': '@',
        'chartHeight': '@'
    },
    templateUrl: 'components/sections/nodeView/nodeStatBox.html',
    controller: ['$scope', '$uibModal', 'nodeStatBoxService', 'nodeViewService',
                function ($scope, $uibModal, nodeStatBoxService, nodeViewService) {

        var expandedChartHeight = 250;
        var statType = $scope.$ctrl.statType;
        $scope.properties = nodeStatBoxService.getStatProperties(statType);
        $scope.options = nodeStatBoxService.makeOptions(statType, $scope.$ctrl.chartHeight);
        $scope.expandedOptions = nodeStatBoxService.makeOptions(statType, expandedChartHeight);
        $scope.nodeStatBoxService = nodeStatBoxService;

        $scope.openModal = function () {
            $uibModal.open({
                templateUrl: 'components/sections/nodeView/nodeStatsModal.html',
                windowTemplateUrl: 'directives/fxWideModal.html',
                resolve: {
                    statIcon: function () { return $scope.properties.icon; },
                    statTitle: function () { return $scope.properties.title; },
                    statOptions: function () { return $scope.expandedOptions; },
                    statData: function () { return $scope.nodeStatBoxService.statData[statType]; }
                },
                controller: 'nodeStatModalCtrl'
            });
        };

        $scope.nodeViewService = nodeViewService;
        $scope.$watch('nodeViewService.getCurrentSelectedNodeKey()', function (nextKey) {
            var selectedKey = nextKey;
            if (nodeViewService.isGroupType(nodeViewService.getCurrentSelectedNodeType())) {
                var primary = nodeViewService.getPrimaryChild(nextKey);

                // If there is a primary we display it otherwise there will just be an empty graph
                if (primary) {
                    selectedKey = primary;
                }
            }

            nodeStatBoxService.setDataFromKey(selectedKey);
        });

        // Set register the watch function with the service if one doesn't exist yet
        var unsetUpdateObject = $scope.$on('socket:update_object', nodeStatBoxService.updateStatObject);
        nodeStatBoxService.setWatch(unsetUpdateObject);
        $scope.$on('$destroy', nodeStatBoxService.unsetWatch);
    }]
});
