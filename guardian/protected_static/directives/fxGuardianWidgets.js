/**
 * fx-guardian-ports
 * -----------
 * callbacks: (none)
 * attrs: description, required, disabled, portConfig, relatedPorts,
 *        enabled, portInfo, port, headerSize, connectionType, tlsConfigId
 * portConfig: minPort, maxPort, monitoredPorts, portsLoaded
 *
 * For setting/resetting a boolean
 */
var fxGuardianPorts = fxApp.component('fxGuardianPorts', {
    templateUrl: 'directives/fxGuardianPorts.html',
    bindings: {
        description: '@',
        required: '@',
        disabled: '@',
        forceTls: '@',
        portConfig: '<',
        relatedPorts: '<',
        portInfo: '<',
        port: '=',
        enabled: '=',
        headerSize: '=',
        connectionType: '=',
        tlsConfigId: '=',
        formInvalid: '=',
    },
    controller: ['$scope', 'guardianService', function($scope, guardianService) {
        var ctrl = $scope.$ctrl;

        ctrl.tlsTypes = guardianService.tlsTypeAPIToHuman;
        ctrl.tlsConfigs = {'-1': 'Default'};
        ctrl.headerSizes = guardianService.sizeHeaderAPIToHuman;

        // Remove unsupported tls types
        if (ctrl.portInfo.disabledTlsTypes.length > 0) {
            // Only delete from a local copy of the global map
            ctrl.tlsTypes = Object.assign({}, ctrl.tlsTypes);
            ctrl.portInfo.disabledTlsTypes.forEach(function (type) {
                delete ctrl.tlsTypes[type];
            });
        }

        // Update the default port if the connection type changed
        $scope.$watch('$ctrl.connectionType', function () {
            if (ctrl.portInfo.defaultClearPort > 0) {
                if (ctrl.connectionType === "Clear") {
                    if (ctrl.port === ctrl.portInfo.defaultPort) {
                        ctrl.port = ctrl.portInfo.defaultClearPort;
                    }
                } else {
                    if (ctrl.port === ctrl.portInfo.defaultClearPort) {
                        ctrl.port = ctrl.portInfo.defaultPort;
                    }
                }
            }
        });

    }],
});

var fxGuardianGroupOptions = fxApp.component('fxGuardianGroupOptions', {
    templateUrl: 'directives/fxGuardianGroupOptions.html',
    bindings: {
        description: '@',
        balancingEnabled: '=',
        guardianPeeringEnabled: '=',
        shouldShowPorts: '=',
        groupType: '<'
    },
    controller: ['$scope', 'guardianService', function($scope, guardianService) {
        var ctrl = $scope.$ctrl;
        ctrl.balancingEnabled = true;
        ctrl.guardianPeeringEnabled = true;
        ctrl.showGuardianPeering = (ctrl.groupType !== 'CARDGROUP');
        
        $scope.$watch('$ctrl.balancingEnabled', function () {
            ctrl.shouldShowPorts = ctrl.balancingEnabled;
        });
    }],
});
