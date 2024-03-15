/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2018
 * @brief Selector object for the node view
 */
fxApp.component('nodeSelector', {
    templateUrl: 'components/sections/nodeView/nodeSelector.html',
    bindings: {
        selectedNodeKey: '<',
    },
    controller: ['$scope', '$window', 'nodeViewService', function($scope, $window, nodeViewService) {
        $scope.nodeViewService = nodeViewService;
        $scope.$watch('$ctrl.selectedNodeKey', function (nextKey) {
            if (nextKey !== nodeViewService.getCurrentSelectedNodeKey()) {
                var nextNode = nodeViewService.getNodeByKey(nextKey);
                if (nextNode) {
                    $window.setNodeSelection(nextNode);
                }
            }
        });
    }]
});
