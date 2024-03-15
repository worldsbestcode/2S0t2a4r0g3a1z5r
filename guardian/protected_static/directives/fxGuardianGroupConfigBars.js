/**
 * @author Tim Brabant <tbrabant@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017
 * @brief Directives for handling the Guardian group/device configuration bars
 *        in the remote devices list view.
 */
fxApp.directive('fxGroupConfigBar', function fxGroupConfigBar() {
    return {
        templateUrl: 'directives/fxGroupConfigBar.html',
        scope: {
            group: '='
        },
        controller: ['$scope', '$uibModal', 'guardianService', 'fxAppDialogService',
                function fxGroupConfigBar($scope, $uibModal, guardianService, fxAppDialogService) {
            /**
             * Determines if this group is logged in or not.
             *
             * @returns True if group is logged in, false otherwise.
             */
            $scope.isLoggedIn = function() {
                return guardianService.isRemoteAuthorized($scope.group.objectType, $scope.group.objectID,
                                                          $scope.group.parentID);
            };

            $scope.propagateCallback = function () {
                guardianService.setSelectedObject($scope.group);
            };

            $scope.disableLoginToGroup = function () {
                canLoginToGroup = $scope.group.children.find(function(child) {
                    return guardianService.canLoginToDevice(child.deviceStatus); 
                });

                // Disable button if there are no devices that can be logged into.
                return canLoginToGroup ? null: true;

            };

            /**
             * Determines if this group is configurable.
             *
             * @returns if this group is configurable.
             */
            $scope.isConfigurable = function() {
                group = $scope.group;
                return !guardianService.isDefaultGroupOrDevice(group.objectType, group.objectID, group.parentID);
            };

            /**
             * Determines if this group is enabled.
             *
             * @return {bool} if this group is enabled.
             */
            $scope.isEnabled = function() {
                return guardianService.isGroupEnabled($scope.group);
            };

            /**
             * Determines if the enable button should be disabled.
             * This group cannot be enabled unless it has devices, and is not monitor-only.
             *
             * @return If the enable button should be disabled.
             */
            $scope.enableDisabled = function() {
                return (!guardianService.hasDevices($scope.group) || 
                        !guardianService.allowsBalancing($scope.group)) ? "true" : "";
            };
            
            /**
             * Determines if the disable button should be disabled.
             * This group can only be disabled if it is not monitor-only.
             *
             * @return If the disable button should be disabled.
             */
            $scope.disableDisabled = function() {
                return (!guardianService.allowsBalancing($scope.group)) ? "true" : "";
            };

            /**
             * Determines if this group can view the enable button.
             *
             * @return if this group can be configured and this group is disabled.
             */
            $scope.viewEnable = function() {
                return !$scope.isEnabled() && $scope.isConfigurable();
            };

            /**
             * Determines if this group can view the disable button.
             *
             * @return if this group can be configured and this group is enabled.
             */
            $scope.viewDisable = function() {
                return $scope.isEnabled() && $scope.isConfigurable();
            };

            /**
             * Enables this group
             */
            $scope.enableGroup = function () {
                guardianService.enableGroup($scope.group);
            };

            /**
             * Disables this group
             */
            $scope.disableGroup = function () {
                guardianService.disableGroup($scope.group);
            };

            /**
             * Adds a device to this group
             */
            $scope.addDevice = function () {
                var modalInstance = $uibModal.open({
                    templateUrl: 'components/sections/config/deviceForm.html',
                    controller: 'addDeviceInstanceCtrl',
                    resolve: {
                        group: function() {
                            return $scope.group;
                        }
                    },
                });

                modalInstance.result.then(function (formdata) {
                    var device = $scope.formDataToDevice(formdata);
                    guardianService.addDevice(device);
                });
            };

            /**
             * Delets this group after confirmation
             */
            $scope.deleteGroup = function() {
                modalOptions = {
                    title: 'Confirm Delete',
                    message: 'Delete group?'
                };

                fxAppDialogService.confirmDialog(modalOptions, function() {
                    guardianService.deleteGroup($scope.group);
                });
            };

            /**
             * Convert the balanced device human readable data to API form.
             *
             * @param formdata the initial form data.
             *
             * @return the device data ready for API create.
             */
            $scope.formDataToDevice = function(formdata) {
                var device = formdata;
                // Force as primary, this group has no children
                if (!guardianService.hasPrimaryDevice($scope.group)) {
                    device.deviceRole = "Primary Device";
                }

                return device;
            };

        }]
    };
});

fxApp.directive('fxDeviceConfigBar', function fxDeviceConfigBar() {
    return {
        templateUrl: 'directives/fxDeviceConfigBar.html',
        scope: {
            device: '='
        },
        controller: ['$scope', '$uibModal', 'guardianService', 'fxAppDialogService',
                function fxDeviceConfigBar($scope, $uibModal, guardianService, fxAppDialogService) {
            /**
             * Determines if this device is logged in or not.
             *
             * @returns True if device (or its parent) are logged in, false otherwise.
             */
            $scope.isLoggedIn = function () {
                return guardianService.isRemoteAuthorized($scope.device.objectType, $scope.device.objectID,
                                                          $scope.device.parentID);
            };

            $scope.hasCommunicationsError = function () {
                return $scope.device.deviceStatus === 'Communications Error' ||
                       $scope.deviceStatus === 'Communications Error (Security Mode)' ? 'true' : null;
            };

            /**
             * Determines if this device is configurable.
             *
             * @returns if this device is configurable
             */
            $scope.isConfigurable = function() {
                device = $scope.device;
                return !guardianService.isDefaultGroupOrDevice(device.objectType, device.objectID, device.parentID);
            };

            $scope.propagateCallback = function () {
                guardianService.setSelectedObject($scope.device);
            };

            /**
             * Determines if this device is enabled.
             *
             * @return if this device is enabled.
             */
            $scope.isEnabled = function() {
                return guardianService.isDeviceEnabled($scope.device);
            }

            $scope.disableLoginToDevice = function () {
                return guardianService.canLoginToDevice($scope.device.deviceStatus) ? null : true;
            };

            /**
             * Determines if the enable button should be disabled.
             * This device cannot be enabled or disabled if it is a primary device.
             *
             * @return if the enable button should be disabled.
             */
            $scope.enableDisabled = function() {
                return guardianService.isPrimaryDevice($scope.device) ? "true" : "";
            };

            /**
             * Determines if this device can view the enable button.
             *
             * @return if this device can be configured and this device is disabled.
             */
            $scope.viewEnable = function() {
                return !$scope.isEnabled() && $scope.isConfigurable();
            };

            /**
             * Determines if this device can view the disable button.
             *
             * @return if this device can be configured and this device is enabled.
             */
            $scope.viewDisable = function() {
                return $scope.isEnabled() && $scope.isConfigurable();
            };

            /**
             * Enables this device
             */
            $scope.enableDevice = function () {
                guardianService.enableDevice($scope.device);
            };

            /**
             * Disables this device
             */
            $scope.disableDevice = function () {
                guardianService.disableDevice($scope.device);
            };

            /**
             * Deletes this device
             */
            $scope.deleteDevice = function () {
                modalOptions = {
                    title: 'Confirm Delete',
                    message: 'Delete device?'
                };

                fxAppDialogService.confirmDialog(modalOptions, function() {
                    guardianService.deleteDevice($scope.device);
                });
            };

            /**
             * Checks if the role of the device can be changed
             * Primary devices cannot change their role
             */
            $scope.changeRoleDisabled = function () {
                return guardianService.isPrimaryDevice($scope.device) ? "true" : "";
            };

            /**
             * Change the role of a device
             */
            $scope.changeRole = function () {
                var modal = $uibModal.open({
                    templateUrl: 'components/sections/config/deviceRoleForm.html',
                    controller: 'changeDeviceRoleInstanceCtrl',
                    resolve: {
                        device: function() {
                            return $scope.device;
                        }
                    },
                });

                modal.result.then(function (formdata) {
                    guardianService.changeDeviceRole(formdata);
                });
            };
        }]
    };
});

fxApp.directive('fxBottomConfigBar', function fxGroupBottomBar() {
    return {
        templateUrl: 'directives/fxBottomConfigBar.html',
        controller: ['$scope', '$uibModal', 'guardianService',
                function fxDeviceConfigBar($scope, $uibModal, guardianService) {
            /**
             * Determines if groups are configurable.
             * @returns if groups are configurable
             */
            $scope.isConfigurable = function() {
                return true;
            };

            /**
             * Adds a new group.
             * This will open a popup to select a group type, then a dialog to configure the group.
             */
            $scope.addGroup = function () {

                var modalType = $uibModal.open({
                    templateUrl: 'components/sections/config/groupTypeForm.html',
                    controller: 'selectGroupTypeInstanceCtrl',
                });

                modalType.result.then(function (groupType) {
                    var modalGroup = $uibModal.open({
                        templateUrl: 'components/sections/config/groupForm.html',
                        controller: 'addGroupInstanceCtrl',
                        resolve: {
                            groupType: function() {
                                return groupType;
                            }
                        },
                    });

                    modalGroup.result.then(function (formdata) {
                        guardianService.addGroup(formdata);
                    });
                });
            };

        }]
    };
});


fxApp.controller('addDeviceInstanceCtrl',
    ['$scope', 'guardianService', 'fxAppStringService', 'fxAppViewService', 'group',
    function($scope, guardianService, fxAppStringService, fxAppViewService, group) {
    $scope.submit = function (result) {
        $scope.$close($scope.formdata);
    };

    $scope.cancel = function (result) {
        $scope.$dismiss('cancel');
    };

    $scope.roleTypes = {
        "Production Device": "Production",
        "Backup Device": "Backup",
    };

    // Do not need to load monitored ports for devices
    $scope.portConfig = {
        minPort: 1024,
        maxPort: 65536,
        // No ports to compare against so they are already loaded and empty
        monitoredPorts: [],
        portsLoaded: true,
    };

    // Set the form data
    $scope.formdata =  {
        objectType: group.childType,
        objectID: "-1",
        parentID: group.objectID,
        ownerID: "-1",
        deviceAddress: "",
        deviceHostname: "",
        roleTypes: $scope.roleTypes,
        deviceRole: "Production Device",
        deviceVerifyHostname: true,
        ports: guardianService.getPortsForType(group.childType),
        groupBalancingEnabled: guardianService.allowsBalancing(group),
        guardianPeeringEnabled: guardianService.allowsGuardianPeering(group),
    };

    guardianService.fixPortsFromParent($scope.formdata.ports, group);

    $scope.hasGuardianHostname = function() {
        return guardianService.hasGuardianHostname(group);
    };

    $scope.hasPrimaryDevice = function() {
        return guardianService.hasPrimaryDevice(group);
    };

    $scope.tlsConfigDisabled = function() {
        return guardianService.hasTlsConfig(group) ? "" : "true";
    };

    $scope.formInvalid = {
        ipaddress: false,
        hostname: false,
        role: false,
        ports: $scope.formdata.ports.reduce(function(result, config) {
            result[config.type] = false;
            return result;
        }, {}),
    };

    $scope.disableSubmit = "true";
    $scope.$watch('formInvalid', function() {
        $scope.disableSubmit = fxAppViewService.objectFalse($scope.formInvalid) ? null : "true";
    }, true);

    $scope.ipRestrict = fxAppStringService.ipv4Restrict;
    $scope.hostnameRegex = fxAppStringService.hostnameRegex;
    $scope.hostnameRestrict = fxAppStringService.hostnameRestrict;
}]);

fxApp.controller('selectGroupTypeInstanceCtrl',
    ['$scope', 'guardianService',
    function($scope, guardianService) {

    // Types allowed to be added
    var allowedTypes = [
        "KMES_GROUP",
        "CARDGROUP",
        "REMOTE_KEY_GROUP",
        "SAS_GROUP",
    ];

    $scope.submit = function (result) {
        $scope.$close($scope.formdata.groupType);
    };

    $scope.cancel = function (result) {
        $scope.$dismiss('cancel');
    };

    $scope.groupTypes = Object.keys(guardianService.groupTypeAPIToHuman)
        .filter(function(key) { return allowedTypes.includes(key); })
        .reduce(function(obj, key) {
            obj[key] = guardianService.groupTypeAPIToHuman[key];
            return obj;
        }, {});

    // Set the form data
    $scope.formdata =  {
        groupTypes: $scope.groupTypes,
        groupType: "KMES_GROUP",
    };
}]);

fxApp.controller('addGroupInstanceCtrl',
    ['$scope', 'guardianService', 'fxAppStringService', 'fxAppViewService', 'groupType',
    function($scope, guardianService, fxAppStringService, fxAppViewService, groupType) {
    $scope.submit = function (result) {
        $scope.$close($scope.formdata);
    };

    $scope.cancel = function (result) {
        $scope.$dismiss('cancel');
    };

    // Setup for port config
    $scope.portConfig = {
        minPort: 1024,
        maxPort: 65536,
        monitoredPorts: [],
        portsLoaded: false,
    };

    $scope.formdata =  {
        objectType: groupType,
        objectID: "-1",
        parentID: "-1",
        ownerID: "-1",
        groupName: "",
        groupDescription: "",
        shouldShowPorts: true,
        ports: guardianService.getPortsForType(groupType),
    };

    // Get monitored ports and update the config when they are fully loaded
    guardianService.getMonitoredPorts(function(ports) {
        $scope.portConfig.monitoredPorts = ports;
        $scope.portConfig.portsLoaded = true;

        function findNextPort(start) {
            var next = start;
            for (; next < $scope.portConfig.maxPort; next++) {
                if ($scope.portConfig.monitoredPorts.indexOf(next) === -1) {
                    break;
                }
            }
            return next;
        }

        // Set the new minimum port
        $scope.portConfig.minPort = findNextPort($scope.portConfig.minPort);

        // Set default values of ports to the next available
        var currentPort = $scope.portConfig.minPort;
        $scope.formdata.ports.forEach(function (config) {
            var nextPort = findNextPort(currentPort);
            config.port = nextPort;
            currentPort = nextPort + 1;
        });
    });

    $scope.tlsConfigDisabled = function() {
        return "";
    };

    $scope.formInvalid = {
        name: false,
        description: false,
        ports: $scope.formdata.ports.reduce(function(result, config) {
            result[config.type] = false;
            return result;
        }, {}),
    };

    $scope.disableSubmit = "true";
    $scope.$watch('formInvalid', function() {
        $scope.disableSubmit = fxAppViewService.objectFalse($scope.formInvalid) ? null : "true";
    }, true);

    $scope.nameRegex = fxAppStringService.nameFieldRegex;
    $scope.descriptionRegex = fxAppStringService.stringFieldRegex;
}]);

fxApp.controller('changeDeviceRoleInstanceCtrl',
    ['$scope', 'device',
    function($scope, device) {

    $scope.roleTypes = {
        "Primary Device": "Primary",
        "Production Device": "Production",
        "Backup Device": "Backup",
    };

    $scope.submit = function (result) {
        $scope.$close($scope.formdata);
    };

    $scope.cancel = function (result) {
        $scope.$dismiss('cancel');
    };

    // Set the form data
    $scope.formdata =  {
        objectType: device.objectType,
        objectID: device.objectID,
        parentID: device.parentID,
        deviceRole: device.deviceRole,
    };
}]);
