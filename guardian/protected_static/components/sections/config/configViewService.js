/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017-2018
 * @brief Service function for handling configuration view logic
 */

/**
 * Service for the configuration view
 */
fxApp.factory('configViewService',
    ['$q', 'fxAppModalService', 'fxAppViewService', 'fxAppStringService', 'guardianService', 'logFetchService',
    function ($q, fxAppModalService, fxAppViewService, fxAppStringService, guardianService, logFetchService) {

    /**
     * Initialize the group for the view
     * @param group the group to init
     */
    function initGroup(group) {
        group.children = [];
        group.isOpen = false;
    }

    /**
     * Initialize the device for the view
     * @param device the device to init
     */
    function initDevice(device) {
        device.isOpen = false;
    }

    /**
     * Get all balanced groups and devices
     * @parm {object}  configModel  Contains the balanced device and group maps
     * @returns {promise} Promise which resolves when the configModel is set with devices and groups
     */
    function getGroupsAndDevices(configModel) {
        var defered = $q.defer();

        // reset the maps
        guardianService.getGroupTypes().forEach(function (groupType) {
            configModel.idToBalancedGroup[groupType] = {};
        });

        guardianService.getDeviceTypes().forEach(function (deviceType) {
            configModel.idToBalancedDevice[deviceType] = {};
        });

        // Manually update the default group to allow downloading system app logs
        updateGroup(configModel, guardianService.defaultGuardianGroup());

        var groupResult = [];
        guardianService.getAllGroups().then(function (groups) {
            groupResult = groups;
            groups.forEach(function (group) {
                updateConfigNodes(configModel, group);
            });

            return guardianService.getAllDevices();
        }).then(function (devices) {
            devices.forEach(function (device) {
                updateConfigNodes(configModel, device);
            });

            defered.resolve();
        });

        return defered.promise;
    }

    /**
     * Formats the data for a device before it is presented to the user
     *
     * @param device Device object
     */
    function formatDeviceValues(device) {
        device.objectDescription = fxAppStringService.capitalizeFirstLetter(device.objectDescription);
    }

    /**
     * Formats the data for a device group before it is presented to the user
     *
     * @param group The device group object
     */
    function formatGroupValues(group) {
        group.objectDescription = fxAppStringService.capitalizeFirstLetter(group.objectDescription);
    }

    /**
     * Updates configuration nodes/groups
     * @param configModel the model to update
     * @param objectData the data to update
     */
    function updateConfigNodes(configModel, objectData) {
        if (!handlesObject(objectData)) {
            return;
        }

        if (guardianService.isDeviceType(objectData.objectType)) {
            updateDevice(configModel, objectData);
        }

        if (guardianService.isGroupType(objectData.objectType)) {
            updateGroup(configModel, objectData);
        }
    }

    /**
     * Checks if this service handles object updates
     * Local guardian devices and application cards are ignored
     * @param objectData the object to update
     * @return true if updating
     */
    function handlesObject(objectData) {
        var startsWith = fxAppStringService.startsWith;
        if (guardianService.isDeviceType(objectData.objectType)) {
            return !startsWith(objectData.deviceAddress, "169.254.");
        }
        else if (guardianService.isGroupType(objectData.objectType)) {
            return true;
        }

        return false;
    }

    /**
     * Updates a device in the model
     * @param configModel the model to update
     * @param newDevice the new device (or new version of an existing device)
     */
    function updateDevice(configModel, newDevice) {
        formatDeviceValues(newDevice);
        addDeviceModelData(newDevice);

        updateChildren(configModel.balancedGroups, newDevice);

        configModel.idToBalancedDevice[newDevice.objectType][newDevice.objectID] = newDevice;
    }

    /**
     * Updates a group in the model
     * @param configModel the model to update
     * @param newGroup the new group (or new version of an existing group)
     */
    function updateGroup(configModel, newGroup) {
        formatGroupValues(newGroup);
        addGroupModelData(newGroup);

        var groups = configModel.balancedGroups;
        var foundGroup = groups.find(function(group) {
            return group.objectID === newGroup.objectID;
        });

        if (foundGroup) {
            copyObject(newGroup, foundGroup);
        } else {
            initGroup(newGroup);
            groups.push(newGroup);
        }

        configModel.idToBalancedGroup[newGroup.objectType][newGroup.objectID] = newGroup;
    }

    /**
     * Converts data from API object representation to model representation
     * @param group the device group to add model values to
     */
    function addGroupModelData(group) {
        group.contentRows = {
            'Description': group.groupDescription ? group.groupDescription : "N/A",
            'Allow Balancing': group.groupBalancingEnabled ? "Yes" : "No",
            'Allow Guardian Peering': group.guardianPeeringEnabled ? "Yes" : "No"
        };

        if (guardianService.allowsBalancing(group)) {
            var params = guardianService.connectionDescriptions(group);
            for (var key in params) {
                group.contentRows[key] = params[key];
            }
        }
    }

    /**
     * Converts data from API object representation to model representation
     * @param device the device device to add model values to
     */
    function addDeviceModelData(device) {
        device.contentRows = {
            'Role': device.currentRole
        };

        var params = guardianService.connectionDescriptions(device);
        for (var key in params) {
            device.contentRows[key] = params[key];
        }
    }

    /**
     * Updates the children of a group with new devices
     * @param groups the groups to update children
     * @param newDevice the new device (or existing device)
     */
    function updateChildren(groups, newDevice) {
        var parentGroup = groups.find(function(group) {
            return newDevice.parentID === group.objectID;
        });

        if (parentGroup) {
            var foundDevice = parentGroup.children.find(function(device) {
                return device.objectID === newDevice.objectID;
            });

            if (foundDevice) {
                copyObject(newDevice, foundDevice);
            } else {
                initDevice(newDevice);
                parentGroup.children.push(newDevice);
            }
        }

    }

    /**
     * Shallow copies an object into another object
     * Leaves values in the original object that are not in the new object
     * @param newObject the object to copy from
     * @param oldObject the object to copy to
     */
    function copyObject(newObject, oldObject) {
        for (var key in newObject) {
            if (typeof(newObject[key]) === "object") {
                copyObject(newObject[key], oldObject[key]);
            } else {
                oldObject[key] = newObject[key];
            }
        }
    }

    /**
     * Removes nodes/groups that no longer exist
     * @param configModel the model to update
     * @param objectData the object that was deleted
     */
    function deleteConfigNodes(configModel, objectData) {
        if (guardianService.isDeviceType(objectData.objectType)) {
            if (objectData.objectID in configModel.idToBalancedDevice[objectData.objectType]) {
                deleteDevice(configModel, objectData);
            }
        }

        if (guardianService.isGroupType(objectData.objectType)) {
            if (objectData.objectID in configModel.idToBalancedGroup[objectData.objectType]) {
                deleteGroup(configModel, objectData);
            }
        }
    }

    /**
     * Clears the model selection if the current object was deleted
     * @param currentSelection the object that is currently selected
     * @param objectData the object that was deleted
     */
    function notifySelectionDeleted(currentSelection, objectData) {
        // Object matches
        // OR the parent matches
        var clear = (currentSelection.objectID === objectData.objectID &&
                     currentSelection.objectType === objectData.objectType) ||
                    (currentSelection.objectID === objectData.parentID &&
                     currentSelection.objectType === guardianService.getGroupType(objectData.objectID));
        if (clear) {
            currentSelection.objectID = null;
            currentSelection.objectType = null;
        }
    }

    /**
     * Deletes an existing device from the model
     * @param configModel the model to update
     * @param objectData the group that was deleted
     */
    function deleteDevice(configModel, objectData) {
        var toDelete = configModel.idToBalancedDevice[objectData.objectType][objectData.objectID];
        notifySelectionDeleted(configModel.currentSelection, toDelete);
        deleteFromChildren(configModel.balancedGroups, toDelete);
        delete configModel.idToBalancedDevice[objectData.objectType][objectData.objectID];
    }

    /**
     * Deletes an existing group from the model
     * @param configModel the model to update
     * @param objectData the group that was deleted
     */
    function deleteGroup(configModel, objectData) {
        // Delete update does not include parent ID but we check against a generic object
        // Which does have a parent ID
        objectData.parentID = "-1";
        notifySelectionDeleted(configModel.currentSelection, objectData);
        deleteFromGroups(configModel.balancedGroups, objectData);
        delete configModel.idToBalancedGroup[objectData.objectType][objectData.objectID];
    }


    /**
     * Deletes a device from the children of a group
     * @param groups the groups to delete from
     * @param toDelete the device to delete
     */
    function deleteFromChildren(groups, toDelete) {
        var parentGroup = groups.find(function(group) {
            return toDelete.parentID === group.objectID;
        });

        if (parentGroup) {
            var index = parentGroup.children.findIndex(function(device) {
                return device.objectID === toDelete.objectID;
            });

            if (index >= 0) {
                parentGroup.children.splice(index, 1);
            }
        }
    }

    /**
     * Deletes a group from the model
     * @param groups the groups to delete from
     * @param objectData the group to delete
     */
    function deleteFromGroups(groups, objectData) {
        var index = groups.findIndex(function(group) {
            return group.objectID === objectData.objectID;
        });

        if (index >= 0) {
            groups.splice(index, 1);
        }
    }

    return {
        getGroupsAndDevices: getGroupsAndDevices,
        guardianService: guardianService,
        updateConfigNodes: updateConfigNodes,
        deleteConfigNodes: deleteConfigNodes,
    };
}]);
