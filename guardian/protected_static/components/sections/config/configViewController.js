/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017-2018
 * @brief Controller for the configuration view
 */

/**
 * Constructor for the configuration view
 * @param {object} $scope
 * @returns {object} A new controller
 */
configViewController.$inject = ['$scope', 'socketio', 'configViewService', 'fxAppService',
                                'logFetchService', 'guardianService', 'fxSpinnerService'];
function configViewController($scope, socketio, configViewService, fxAppService,
                              logFetchService, guardianService, fxSpinnerService) {

    $scope.guardianService = guardianService;
    $scope.fxAppService = fxAppService;

    $scope.localProductName = guardianService.localProductName()

    // The column mapping holds static display constants
    $scope.mappings = {
        groupHeaderMapping: {
            groupName: 'Name',
            objectDescription: 'Type',
            groupState: 'State'
        },
        groupContentMapping: {
            groupDescription: 'Description'
        },
        deviceHeaderMapping: {
            deviceAddress: 'IP Address',
            deviceSerial: 'Serial',
            objectDescription: 'Type',
            deviceStatus: 'Status'
        },
        deviceContentMapping: {
            deviceRole: 'Role',
            statTPS: 'Transactions per second'
        },
    };

    $scope.$on('socket:delete_object', function(ev, data) {
        var objectData = data.objectData;
        configViewService.deleteConfigNodes($scope.configModel, objectData);
    });

    $scope.$on('socket:update_object', function(ev, data) {
        var objectData = data.objectData;
        configViewService.updateConfigNodes($scope.configModel, objectData);
    });


    // The configuration model holds all objects
    $scope.configModel = {
        currentSelection: {},
        balancedGroups: [],
        idToBalancedDevice: {},
        idToBalancedGroup: {},
    };

    configViewService.getGroupsAndDevices($scope.configModel).then(
        function() {
            /* Once the config view has loaded remove the spinner*/
            fxSpinnerService.remove('configSpinner');
        }
    );

};

fxApp.controller('configViewController', configViewController);
