fxApp.component('nodeInfoBox', {
    templateUrl: 'components/sections/nodeView/nodeInfoBox.html',
    controller: ['$scope', '$uibModal', 'fxAppStringService', 'nodeViewService',
                 function($scope, $uibModal, fxAppStringService, nodeViewService) {

        $scope.nodeViewService = nodeViewService;
        $scope.openModal = function() {
            $uibModal.open({
                templateUrl: 'components/sections/nodeView/nodeInfoModal.html',
                controller:'nodeInfoModalCtrl'
                }
            )
        };
    }]
});

fxApp.controller('nodeInfoModalCtrl', ['$scope', 'nodeViewService',
                                       function($scope, nodeViewService) {

    $scope.nodeViewService = nodeViewService;
    $scope.cancel = function () {
        $scope.$dismiss('cancel');
    };
}]);

fxApp.component('nodeInfo', {
    templateUrl: 'components/sections/nodeView/nodeInfo.html',
    controller: ['$scope', '$uibModal','socketio', 'nodeViewService', 'fxAppStringService',
                 function($scope, $uibModal, socketio, nodeViewService, fxAppStringService) {

        $scope.nodeImgSrc = nodeViewService.getCurrentSelectedNodeImgSrc()
        $scope.nodeInfo = nodeViewService.getCurrentSelectedNodeInfo()

        $scope.$watchGroup([
                nodeViewService.getCurrentSelectedNodeImgSrc.bind(null),
                nodeViewService.getCurrentSelectedNodeInfo.bind(null)
            ], function(newValues) {
                $scope.nodeImgSrc = newValues[0];
                $scope.nodeInfo = newValues[1];
            }
        );

        // Update group map to include device
        function updateGroupMaps (nodeKey) {
            var deviceData = nodeViewService.deviceValueMap[nodeKey];
            var parentKey = nodeViewService.getParentNodeKey(deviceData);
            if(!(parentKey in nodeViewService.groupValueMap)) {
                nodeViewService.groupValueMap[parentKey] = [];
            }
            if (!nodeViewService.groupValueMap[parentKey].includes(nodeKey)) {
                nodeViewService.groupValueMap[parentKey].push(nodeKey);
            }
        }

        // Updates devices uptime and status fields
        function updateDynamicDeviceInfo (nodeKey, deviceData) {
            if (nodeViewService.getGroupTypes().includes(nodeViewService.getCurrentSelectedNodeType())){
                // Clear the update status and uptime fields if group is selected
                $scope.dynamicNodeInfo = "";
            } else if (nodeKey === nodeViewService.getCurrentSelectedNodeKey()) {
                $scope.dynamicNodeInfo = "Status: " + deviceData.deviceStatus + "\n" +
                                         "Uptime: " + fxAppStringService.secondsToDayHourMinuteString(deviceData.statUptime);
            }
        }

        //Update device and group maps and dynamic information on the socket update
        $scope.$on('socket:update_object', function(ev, data) {
            var objectData = data.objectData;
            var nodeKey = nodeViewService.getNodeKey(objectData);

            // Add devices to the device map
            if (!(nodeKey in nodeViewService.deviceValueMap)) {
                nodeViewService.deviceValueMap[nodeKey] = angular.copy(objectData);
            }
            updateGroupMaps(nodeKey);
            updateDynamicDeviceInfo(nodeKey, objectData);
        });
    }]
});
