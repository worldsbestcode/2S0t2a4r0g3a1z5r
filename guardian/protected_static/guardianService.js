/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017-2018
 * @brief Functions shared among multiple guardian views
 */

fxApp.factory('guardianService',
  [
    '$q',
    '$http',
    'fxAppService',
    'fxAppViewService',
    'fxAppModalService',
    'fxAppObjectService',
    '$uibModal',
    'fxAppStringService',
    'fxCookieService',
    function(
      $q,
      $http,
      fxAppService,
      fxAppViewService,
      fxAppModalService,
      fxAppObjectService,
      $uibModal,
      fxAppStringService,
      fxCookieService
    )
{
    // Which item (group, device) is "active" in the config view.
    var selectedObject = {
        object: null,
        objectDisplayName: '',
        objectID: '',
        objectType: '',
        parentID: '',
    };

    var loginContextString = "";
    var authorizedIDs = {
        groups: [],
        devices: []
    };

    // Cache of data shared to Vue about the selected object
    var selectionState = {
        authorized: false,
        objectID: '-1',
        parentID: '-1',
        objectType: null,
    };

    var deviceTypeToGroupType = {
        'CARD': 'CARDGROUP',
        'IRIS_DEVICE': 'IRIS_GROUP',
        'KMES_DEVICE': 'KMES_GROUP',
        'LOCAL_GUARDIAN_DEVICE': 'LOCAL_GUARDIAN_GROUP',
        'REMOTE_KEY_DEVICE': 'REMOTE_KEY_GROUP',
        'SAS_DEVICE': 'SAS_GROUP'
    };

    /*Color mappings for balanced devices and groups*/
    var stateColors = {
        'Connection Setup' : 'ok',
        'Additional Connection Setup': 'ok',
        'Connected (Querying)': 'ok',
        'Connected (Processing)': 'ok',
        'Connected (Out of Sync)':'caution',
        'Connected (Syncing)': 'ok',
        'Communications Error': 'error',
        'Communications Error (Security Mode)': 'error',
        'Balancing Disabled': 'disabled',
        'Disabled': 'disabled',
        'Disabled (Monitor Only)': 'disabled',
        'Paused': 'caution',
        'Running': 'ok'
    };

    var balancedDeviceTypes = Object.keys(deviceTypeToGroupType);
    var balancedGroupTypes = Object.keys(deviceTypeToGroupType).map(function (device) {
        return deviceTypeToGroupType[device];
    });

    var groupTypeAPIToHuman = {
        "CARDGROUP": "Hardware Security Module",
        "IRIS_GROUP": "Authenticrypt",
        "KMES_GROUP": "Key And Certificate Management",
        "LOCAL_GUARDIAN_GROUP": "Local Machine",
        "REMOTE_KEY_GROUP": "Remote Key Injection",
        "SAS_GROUP": "Secure Storage",
    };

    var tlsTypeAPIToHuman= {
        'TLS': 'TLS',
        'AnonTLS': 'Anonymous TLS',
        'Clear': 'Clear',
    };

    var portTypeAPIToHuman= {
        "Admin": "Administration",
        "ExcryptAuth": "Excrypt Authentication",
        "Excrypt RKL": "Excrypt RKL",
        "Production": "Excrypt/Standard",
        "HTTP": "Web",
        "Peer": "Peer",
        "Host API": "Host API",
        "International": "International",
        "Pilot": "Smart Token Perso",
    };

    var sizeHeaderAPIToHuman = {
        'None': 'None',
        '2 Byte': 'Two Byte Size',
        '4 Char': 'Four Char Size'
    };

    var localGuardianGroupType = 'LOCAL_GUARDIAN_GROUP';
    var localGuardianGroupID = '2';
    var PRIMARY_TYPE = 'Primary Device';

    function getSelectedObject() {
        return selectedObject.object;
    }

    /**
     * Group type accessor
     * Returns a list of balanced device group types
     */
    function getGroupTypes() {
        return balancedGroupTypes.slice();
    }

    /**
     * Device type accessor
     * @return {array}  A list of balanced device types
     */
    function getDeviceTypes() {
        return balancedDeviceTypes.slice();
    }

    /**
     * Checks if the object type is a device type
     *
     * @param {string} objectType The object type to check
     *
     * @return true=It is a device type, false=It is not a device type
     */
    function isDeviceType(objectType) {
        return balancedDeviceTypes.indexOf(objectType) >= 0;
    }

    /**
     * Check if the type is a group type
     * @param {string}  objectType  The type to check
     * @return True if the type is a group type false otherwise
     */
    function isGroupType(objectType) {
        return balancedGroupTypes.indexOf(objectType) >= 0;
    }

    /**
     * Get Group Type
     * @param {string}  objectType  The object type to transform into a group type
     * @return {string}  groupType  The transformed type. Null if not a device or group type
     */
    function getGroupType(objectType) {
        var groupType = null;
        if (objectType in deviceTypeToGroupType) {
            groupType = deviceTypeToGroupType[objectType];
        } else if (isGroupType(objectType)) {
            groupType = objectType;
        }

        return groupType;
    }

    /**
     * Return an object that represents the local guardian group
     * @return {object}  The local guardian group
     */
    function defaultGuardianGroup() {
        return {
            childType: 'LOCAL_GUARDIAN_DEVICE',
            groupName: 'Local Machine',
            groupState: 'Running',
            objectDescription: 'local Guardian group',
            objectID: localGuardianGroupID,
            objectType: localGuardianGroupType
        };
    }

    /**
     * Retrieves the product name to display for this guardian device
     *
     * @return The product name
     */
    function localProductName() {
        return 'Guardian Series 3';
    }
    
    /**
     * Retrieves the node name for this guardian device.
     *
     * @return The name of the local Guardian node.
     */
    function localProductNodeName() {
        return 'Guardian';
    }

    /**
     * Return true if the given parameters match the default group
     * @param {string}  objectType  The object type string
     * @param {string}  objectID  The object id as a string
     * @return {boolean}  True if it is a default guardian group
     */
    function isDefaultGroup(objectType, objectID) {
        return objectType === localGuardianGroupType && objectID === localGuardianGroupID;
    }

    /**
     * Check if the object is a child of the default group
     * @param {string}  objectType  The object type of the child device
     * @param {string}  parentID  The id of the object's parent
     * @return {boolean}  True if the object is a child of the default group
     */
    function isDefaultDevice(objectType, parentID) {
        return objectType === 'LOCAL_GUARDIAN_DEVICE' && parentID === localGuardianGroupID;
    }

    /**
     * Check if the object is a child of the default group or the default group
     * @param {string}  objectType  The object type string
     * @param {string}  objectID  The object id as a string
     * @param {string}  parentID  The id of the object's parent
     */
    function isDefaultGroupOrDevice(objectType, objectID, parentID) {
        return isDefaultGroup(objectType, objectID) || isDefaultDevice(objectType, parentID);
    }

    /**
     * Get a list of all the group results of every type
     * @return {promise}  Containing the result list
     */
    function getAllGroups() {
        return fxAppViewService.getAllObjectsForTypes(balancedGroupTypes);
    }

    /**
     * Get a list of all the device results of every type
     * @return {promise}  Containing the result list
     */
    function getAllDevices() {
        return fxAppViewService.getAllObjectsForTypes(balancedDeviceTypes);
    }

    /**
     * Get connection descriptions for a connection parameter container
     * @param {object}  container  The connection mapping
     */
    function connectionDescriptions(container) {
        var MAX_CONN = 5;
        var properties = {
            'Port': 'Listen Port',
            'Transport': 'Transport Type',
            'Allowed': 'Connection Allowed'
        };

        /**
         * Get the display name for the specific connection
         * @param {string}  prefix  The connection prefix
         * @param {object}  container  The connection holder
         */
        function displayName(prefix, container) {
            var nameProperty = prefix + 'Name';
            var name;
            if (container.hasOwnProperty(nameProperty)) {
                name = container[nameProperty];
            }

            return name;
        }

        var descriptions = {};
        for(var i = 0; i < MAX_CONN; i++) {
            var prefix = 'connparam' + i;
            var name = displayName(prefix, container);
            if (name) {
                Object.keys(properties).forEach(function (property) {
                    var displayProperty = name + ' ' + properties[property];
                    descriptions[displayProperty] = container[prefix + property];
                });
            }
        }

        return descriptions;
    }

    /**
     * Check if the current selected object is a group
     */
    function isSelectionGroup() {
        return isGroupType(selectedObject.objectType);
    }

    /**
     * Set the selected object
     * @param {object}  nextObject  The new selected object
     */
    function setSelectedObject(nextObject) {
        selectedObject.object = nextObject;
        selectedObject.objectType = nextObject.objectType;
        selectedObject.objectID = nextObject.objectID;
        selectedObject.parentID = nextObject.parentID;

        // Name last because services watch this.
        if (isSelectionGroup()) {
            selectedObject.objectDisplayName = nextObject.groupName;
        } else {
            selectedObject.objectDisplayName = nextObject.deviceAddress;
        }

        fxAppService.setRightSidebarShown(true);

        selectionState.authorized = isObjectAuthorized(nextObject);
        selectionState.objectID = nextObject.objectID;
        selectionState.parentID = nextObject.parentID;
        selectionState.objectType = nextObject.objectType;
    }

    /**
     * Check if a remote object is authorized
     * @param {string}  objectType  The type of the object
     * @param {string}  objectID  The object id to check for the index
     * @param {string}  parentID  The parent object to check for authorization
     * @return {boolean}  True if authorized false otherwise
     */
    function isRemoteAuthorized(objectType, objectID, parentID) {
        if (isDefaultGroupOrDevice(objectType, objectID, parentID)) {
            return true;
        }

        if (isGroupType(objectType)) {
            return authorizedIDs.groups.indexOf(objectID) >= 0;
        }

        return authorizedIDs.groups.indexOf(parentID) >= 0 || authorizedIDs.devices.indexOf(objectID) >= 0;
    }

    function isObjectAuthorized(toCheck) {
        return isRemoteAuthorized(toCheck.objectType, toCheck.objectID, toCheck.parentID);
    }

    /**
     * Check if the current device or group is logged in
     * @return {boolean}  True if authorized false otherwise
     */
    function isSelectionAuthorized() {
        return isRemoteAuthorized(selectedObject.objectType, selectedObject.objectID, selectedObject.parentID);
    }

    /**
     * Get the name of the selected object
     */
    function getSelectionName() {
        return selectedObject.objectDisplayName;
    }

    /**
     * Updates an object in a list with the same id or prepends it to the list if not present
     *
     * @param array The array to update
     * @param object The object to update or insert with
     */
    function updateObjectInArray(array, object) {
        var found = array.some(function(current) {
            if (current.objectID === object.objectID) {
                Object.assign(current, object);

                return true;
            }

            return false;
        });

        if (!found) {
            array.unshift(object);
        }
    }

    /**
     * Removes an object from an array with a matching id
     *
     * @param array The array to traverse
     * @param id The id of the object to remove
     */
    function removeObjectFromArray(array, id) {
        for(var i = 0; i < array.length; i++) {
            if (array[i].objectID == id) {
                array.splice(i, 1);
            }

            break;
        }
    }

    /**
     * Set the authorized id list
     */
    function setAuthorizedIDs(updatedIDs) {
        if ('devices' in updatedIDs) {
            authorizedIDs.devices = updatedIDs.devices;
        }

        if ('groups' in updatedIDs) {
            authorizedIDs.groups = updatedIDs.groups;
        }

        selectionState.authorized = isSelectionAuthorized();
    }

    /**
     * Initialize the list of balanced devices/groups that are already logged in
     */
    function initAuthorizedIDs() {
        $http.get(window.apipath("/logininfo"), {responseType: 'text'}).then(function(response) {
          ids = fxCookieService.getAuthorizedRemoteObjectIDs();
          if (ids !== undefined)
            setAuthorizedIDs(ids);
        });
    }

    /**
     * Check if the current selection is a default group or device
     */
    function isSelectionDefault() {
        return isDefaultGroupOrDevice(selectedObject.objectType, selectedObject.objectID, selectedObject.parentID);
    }

    /*
     * Get the class which will set the text
     * color for a group or device's state.
     *
     * @param state Group state or device status
     */
    function getStateClass(state) {
        return stateColors[state];
    }

    /*
     * Returns wether or not a device is able to be
     * logged into.
     */
    function canLoginToDevice(deviceStatus) {
        var canLogin = true;
        if (fxAppStringService.startsWith(deviceStatus, "Communications") ||
            fxAppStringService.includes(deviceStatus, "Connection Setup")) {
            canLogin = false;
        }
        return canLogin;
    }


    /**
     * Check if the current selection is a default device.
     */
    function isSelectionDefaultDevice() {
        return isDefaultDevice(selectedObject.objectType, selectedObject.parentID);
    }

    /**
     * Checks if the group uses hostnames.
     * As more devices are updated to use web, add them here.
     * @param group the input group
     * @return if the group has a hostname.
     */
    function hasGuardianHostname(group) {
        return group.objectType === "KMES_GROUP";
    }

    /**
     * Checks if the group has any devices.
     * @param group the group to check.
     * @return if the group has any devices.
     */
    function hasDevices(group) {
        return group.children.length > 0;
    }
    
    /**
     * Checks to see if balancing is allowed for a group (if the group
     * is monitor-only, it is not).
     * 
     * @param {object} group Group to check.
     */
    function allowsBalancing(group) {
        return group.groupBalancingEnabled;
    }

    /**
     * Checks to see if guardian peeringis allowed for a group 
     * 
     * @param {object} group Group to check.
     */
    function allowsGuardianPeering(group) {
        return group.guardianPeeringEnabled;
    }

    /**
     * Checks if the group has a configured primary device
     * @param group the group to check.
     * @return if the group has a configured primary device
     */
    function hasPrimaryDevice(group) {
        return group.groupPrimaryDevice !== "-1";
    }

    /**
     * Checks if the group is enabled.
     * @param group the group to check.
     * @return if the group is not disabled.
     */
    function isGroupEnabled(group) {
        // Running, Syncing, and Paused are all considered Enabled
        return group.groupState !== "Disabled";
    }

    /**
     * Checks if the device is enabled.
     * There are multiple possible strings that include disabled, so just check for Disabled in the status.
     * @param device the device to check.
     * @return if the device is enabled.
     */
    function isDeviceEnabled(device) {
        return device.deviceStatus.indexOf("Disabled") === -1;
    }

    /**
     * Checks if the device is a primary device or temporary primary device.
     * @param device the device to check.
     * @return if the device is of the primary type.
     */
    function isPrimaryDevice(device) {
        return device && fxAppStringService.startsWith(device.deviceRole, PRIMARY_TYPE);
    }

    /**
     * Checks if devices of this group can configure TLS settings
     * @param group the group to check
     * @return if the group is not an application device
     */
    function hasTlsConfig(group) {
        return group.objectType === "CARDGROUP";
    }

    /**
     * Sets the default values for devices
     * @param ports the ports config to update
     */
    function setDevicePortDefaults(ports) {
        var default_config = {
            enabled: true,
            required: true,
            headerSize: "None",
            connectionType: "TLS",
            tlsConfigId: "-1",
            defaultClearPort: -1,
            disabledTlsTypes: [],
        };

        Object.keys(default_config).forEach(function (key) {
            ports.forEach(function (config) {
                if (config[key] === undefined) {
                    config[key] = default_config[key];
                }
            });
        });

        ports.forEach(function (config) {
            config.name = portTypeAPIToHuman[config.type];
            config.port = config.defaultPort;
        });
    }

    /**
     * Sets the default values for groups
     * The default port is set to the port value
     * @param ports the ports config to update
     */
    function setGroupPortDefaults(ports) {
        var default_config = {
            enabled: true,
            required: false,
            headerSize: "None",
            connectionType: "Clear",
            tlsConfigId: "-1",
            port: -1,
            defaultClearPort: -1,
            disabledTlsTypes: [],
        };

        Object.keys(default_config).forEach(function (key) {
            ports.forEach(function (config) {
                if (config[key] === undefined) {
                    config[key] = default_config[key];
                }
            });
        });

        ports.forEach(function (config) {
            config.name = portTypeAPIToHuman[config.type];
        });
    }

    /**
     * Gets the ports config for a given type
     * @param type the object type
     * @return the ports config for the given object type
     */
    function getPortsForType(type) {
        var ports = [];
        if (type === 'CARD') {
            ports.push({
                type: "Production",
                defaultPort: 9100,
                defaultClearPort: 9000,
            });
            ports.push({
                type: "Admin",
                defaultPort: 9009,
                defaultClearPort: 9010,
            });
            ports.push({
                type: "International",
                defaultPort: 9105,
                defaultClearPort: 9005,
                enabled: false,
            });
        } else if (type === 'IRIS_DEVICE') {
            ports.push({
                type: "Host API",
                defaultPort: 2001,
                forceTls: true,
            });
            ports.push({
                type: "Pilot",
                defaultPort: 1024,
            });
            ports.push({
                type: "ExcryptAuth",
                defaultPort: 1024,
            });
        } else if (type === 'KMES_DEVICE') {
            ports.push({
                type: "Host API",
                defaultPort: 2001,
                forceTls: true,
            });
            ports.push({
                type: "Peer",
                defaultPort: 7001,
                forceTls: true,
            });
            ports.push({
                type: "HTTP",
                defaultPort: 8081,
            });
        } else if (type === 'REMOTE_KEY_DEVICE') {
            ports.push({
                type: "Host API",
                defaultPort: 2001,
                forceTls: true,
            });
            ports.push({
                type: "Excrypt RKL",
                defaultPort: 5001,
            });
        } else if (type === 'SAS_DEVICE') {
            ports.push({
                type: "Host API",
                defaultPort: 2001,
                forceTls: true,
            });
        } else if (type === 'CARDGROUP') {
            ports.push({
                type: "Production",
            });
            ports.push({
                type: "International",
                enabled: false,
            });
            ports.push({
                type: "HTTP",
            });
        } else if (type === 'IRIS_GROUP') {
            ports.push({
                type: "Host API",
            });
            ports.push({
                type: "Pilot",
            });
            ports.push({
                type: "Excrypt Authentication",
            });
        } else if (type === 'KMES_GROUP') {
            ports.push({
                type: "Host API",
            });
            ports.push({
                type: "HTTP",
                disabledTlsTypes: ["Clear"],
                connectionType: "AnonTLS",
            });
        } else if (type === 'REMOTE_KEY_GROUP') {
            ports.push({
                type: "Host API",
            });
            ports.push({
                type: "Excrypt RKL",
            });
            ports.push({
                type: "HTTP",
            });
        } else if (type === 'SAS_GROUP') {
            ports.push({
                type: "Host API",
            });
        }

        if (isDeviceType(type)) {
            setDevicePortDefaults(ports);
        }

        if (isGroupType(type)) {
            setGroupPortDefaults(ports);
        }

        return ports;
    }

    function fixPortsFromParent(ports, group) {
        ports.forEach(function (config) {
            if (config.type === "International") {
                config.enabled = group.groupInternationalPortAllowed;
            }
            if (config.type === "HTTP") {
                // Currently we force HTTP proxy for KMES device
                config.enabled = true;
            }
        });
    }

    // Start of API functions
    function addGroup(group) {
        fxAppObjectService.addObject(group);
    }

    function addDevice(device) {
        fxAppObjectService.addObject(device);
    }

    function deleteGroup(group) {
        fxAppObjectService.deleteObject(group);
    }

    function deleteDevice(device) {
        fxAppObjectService.deleteObject(device);
    }

    function enableGroup(group) {
        var newGroup = {
            objectID: group.objectID,
            objectType: group.objectType,
            groupState: "Enabled",
        };

        fxAppObjectService.modifyObject(newGroup);
    }

    function disableGroup(group) {
        var newGroup = {
            objectID: group.objectID,
            objectType: group.objectType,
            groupState: "Disabled",
        };

        fxAppObjectService.modifyObject(newGroup);
    }

    function enableDevice(device) {
        var newDevice = {
            objectID: device.objectID,
            objectType: device.objectType,
            deviceStatus: "Enabled",
        };

        fxAppObjectService.modifyObject(newDevice);
    }

    function disableDevice(device) {
        var newDevice = {
            objectID: device.objectID,
            objectType: device.objectType,
            deviceStatus: "Disabled",
        };

        fxAppObjectService.modifyObject(newDevice);
    }

    function changeDeviceRole(device) {
        if (device.deviceRole === PRIMARY_TYPE) {
            // If the device is being assigned as primary,
            // instead modify the group to have a new primary device
            var newGroup = {
                objectID: device.parentID,
                objectType: getGroupType(device.objectType),
                groupPrimaryDevice: device.objectID,
            };

            fxAppObjectService.modifyObject(newGroup);
        } else {
            var newDevice = {
                objectID: device.objectID,
                objectType: device.objectType,
                deviceRole: device.deviceRole,
            };

            fxAppObjectService.modifyObject(newDevice);
        }
    }

    initAuthorizedIDs();

    return {
        // Utility functions
        defaultGuardianGroup: defaultGuardianGroup,
        getGroupType: getGroupType,
        getGroupTypes: getGroupTypes,
        getDeviceTypes: getDeviceTypes,
        isGroupType: isGroupType,
        isDeviceType: isDeviceType,
        getAllGroups: getAllGroups,
        getAllDevices: getAllDevices,
        getSelectionName: getSelectionName,
        isSelectionAuthorized: isSelectionAuthorized,
        isSelectionDefault: isSelectionDefault,
        isSelectionDefaultDevice: isSelectionDefaultDevice,
        isDefaultGroup: isDefaultGroup,
        isDefaultGroupOrDevice: isDefaultGroupOrDevice,
        isRemoteAuthorized: isRemoteAuthorized,
        isObjectAuthorized: isObjectAuthorized,
        isSelectionGroup: isSelectionGroup,
        connectionDescriptions: connectionDescriptions,
        setAuthorizedIDs: setAuthorizedIDs,
        setSelectedObject: setSelectedObject,
        selectedObject: selectedObject,
        loginContextString: loginContextString,
        getSelectedObject: getSelectedObject,
        updateObjectInArray: updateObjectInArray,
        removeObjectFromArray: removeObjectFromArray,
        isGroupEnabled: isGroupEnabled,
        isDeviceEnabled: isDeviceEnabled,
        isPrimaryDevice: isPrimaryDevice,
        hasDevices: hasDevices,
        hasPrimaryDevice: hasPrimaryDevice,
        hasGuardianHostname: hasGuardianHostname,
        hasTlsConfig: hasTlsConfig,
        tlsTypeAPIToHuman: tlsTypeAPIToHuman,
        sizeHeaderAPIToHuman: sizeHeaderAPIToHuman,
        groupTypeAPIToHuman: groupTypeAPIToHuman,
        getStateClass: getStateClass,
        canLoginToDevice: canLoginToDevice,
        localProductName: localProductName,
        localProductNodeName: localProductNodeName,
        getPortsForType: getPortsForType,
        fixPortsFromParent: fixPortsFromParent,
        allowsBalancing: allowsBalancing,
        allowsGuardianPeering: allowsGuardianPeering,

        // External API
        addGroup: addGroup,
        addDevice: addDevice,
        deleteGroup: deleteGroup,
        deleteDevice: deleteDevice,
        enableGroup: enableGroup,
        enableDevice: enableDevice,
        disableGroup: disableGroup,
        disableDevice: disableDevice,
        changeDeviceRole: changeDeviceRole,

        getMonitoredPorts: fxAppObjectService.getMonitoredPorts,
        majorKeyChecksums: fxAppObjectService.getMajorKeyChecksums,

        // Only to be called from Vue shared link
        vueOnlySelectionState: selectionState,
    };
}]);
