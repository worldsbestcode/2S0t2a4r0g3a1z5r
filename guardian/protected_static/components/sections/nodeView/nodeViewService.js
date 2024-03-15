/**
 * Provides commonly used functions for the CSR view
 *
 * @returns {object}    helper functions injected into the CSR view controller
 */

var nodeViewService = fxApp.factory('nodeViewService',
    ['$http', '$q', '$document', '$window', 'fxAppService', 'fxAppViewService', 'fxAppStringService', 'guardianService', 'filterService',
    function($http, $q, $document, $window, fxAppService, fxAppViewService, fxAppStringService, guardianService, filterService) {
        // Default current node to Guardian device
        var currentNode = {};
        var currentSelectedNodeInfo = "";
        var currentSelectedNodeImgSrc = '/guardian/static/images/guardian-3.png';
        var deviceValueMap = {};
        var groupValueMap = {};
        var cachedGraph = { nodes:[], links:[] };
        var nodeNames = [];

        /**
         * Manage the layout for the node view content div
         *
         * @param   {HTMLElement}    nodeViewContent - an element referenced in the DOM
         * @returns {function}       updater function to be called when DOM is ready
         */
        function manageNodeViewContentLayout(nodeViewContent) {
            // Get dimensions
            var width = nodeViewContent.clientWidth;
            var height = nodeViewContent.clientHeight;

            // Thresholds in pixels
            var collapseWidth = 1320;
            var collapseHeight = 600;

            // Layout elements
            var leftColId = '#node-view-content-left-column';
            var leftColTopId = '#node-view-content-left-column-top';
            var leftColBottomId = '#node-view-content-left-column-bottom';
            var rightColId = '#node-view-content-right-column';

            // Column CSS
            var collapseColumnClass = 'node-view-content-column-collapse';
            var collapseLeftColumnTopClass = 'node-view-content-left-column-top-collapse';
            var collapseLeftColumnBottomClass = 'node-view-content-left-column-bottom-collapse';

            // Get column elements
            var leftCol = $document.find(leftColId);
            var leftColTop = $document.find(leftColTopId);
            var leftColBottom = $document.find(leftColBottomId);
            var rightCol = $document.find(rightColId);

            // Determine when to collapse the view
            if (width < collapseWidth || height < collapseHeight) {
                // Collapse the layout
                leftCol.addClass(collapseColumnClass);
                rightCol.addClass(collapseColumnClass);

                // Rearrange left column
                leftColTop.addClass(collapseLeftColumnTopClass);
                leftColBottom.addClass(collapseLeftColumnBottomClass);
                rightCol.prepend(leftColBottom, rightCol.firstChild);
            }
            else {
                // Expand the layout
                leftCol.removeClass(collapseColumnClass);
                rightCol.removeClass(collapseColumnClass);

                // Restore left column
                leftColTop.removeClass(collapseLeftColumnTopClass);
                leftColBottom.removeClass(collapseLeftColumnBottomClass);
                leftCol.append(leftColBottom);
            }
        }

        /**
         * Makes a request for device groups
         *
         * @param   {string}    statusStr - e.g. Pending, Denied, etc.
         * @returns {promise}   resolved upon receiving the response
         */
        function getDeviceGroups() {
            var deferred = $q.defer();

            var deviceGroups = guardianService.getGroupTypes();
            var deviceGroup_results = [];

            var i = 0;
            deviceGroups.forEach(function(bdg) {
                var bdgQuery = {
                    "method": "retrieve",
                    "objectType": "Filter",
                    "quantity": 100,
                    "request": {
                        "manager": bdg,
                        "chunk": 0,
                        "chunkSize": 100,
                        "chunkCount": 1,
                        "matchCount": 1,
                        "flags": [],
                        "filterType": "RESULTS",
                        "sortAscending": false,
                        "distinctOn": "",
                        "objectIDs": {}
                    }
                };

                $http.post(window.apipath('/object'), bdgQuery).success(function(data) {
                    if (bdg in data.objectData) {
                        async.filter(data.objectData[bdg], function(node, callback) {
                            // If this is not the application group object
                            nodejs = JSON.parse(node);
                            callback(null, nodejs.objectID > 1);
                        }, function(error, results) {
                            deviceGroup_results = deviceGroup_results.concat(results.map(function(node_data) {
                                return JSON.parse(node_data);
                            }));

                            ++i;
                            if (i === deviceGroups.length) {
                                deferred.resolve(deviceGroup_results);
                            }
                        });
                    }
                });
            });

            return deferred.promise;
        }

        /**
         * Makes a request for devices
         *
         * @param   {string}    statusStr - e.g. Pending, Denied, etc.
         * @returns {promise}   resolved upon receiving the response
         */
        function getDevices() {
            var deferred = $q.defer();

            var devices = guardianService.getDeviceTypes();
            var device_results = [];

            var i = 0;
            devices.forEach(function(bd) {
                var bdQuery = {
                    "method": "retrieve",
                    "objectType": "Filter",
                    "quantity": 100,
                    "request": {
                        "manager": bd,
                        "chunk": 0,
                        "chunkSize": 100,
                        "chunkCount": 1,
                        "matchCount": 1,
                        "flags": [],
                        "filterType": "RESULTS",
                        "sortAscending": false,
                        "distinctOn": "",
                        "objectIDs": {}
                    }
                };

                $http.post(window.apipath('/object'), bdQuery).success(function(data) {

                    if (bd in data.objectData) {
                        async.filter(data.objectData[bd], function(node, callback) {
                            // If this is not the application group object
                            nodejs = JSON.parse(node);
                            callback(null, nodejs.application === false);
                        }, function(error, results) {
                            device_results = device_results.concat(results.map(function(node_data) {
                                return JSON.parse(node_data);
                            }));

                            ++i;
                            if (i === devices.length) {
                                deferred.resolve(device_results);
                            }
                        });
                    }
                });
            });

            return deferred.promise;
        }

        function createGroupNode(node, id) {
            var label = node.groupName + ' (Group)';

            return {
                connections: guardianService.connectionDescriptions(node),
                name: label,
                nodeKey: getNodeKey(node),
                status: node.groupState,
                objectID: node.objectID,
                parentID: node.parentID,
                objectDescription: node.objectDescription,
                objectType : node.objectType,
                parentType : node.parentType,
                group: id,
                groupName: node.groupName
            };
        }

        function createDeviceNode(node, id) {
            return {
                name: node.deviceName,
                nodeKey: getNodeKey(node),
                address: node.deviceAddress,
                status: node.deviceStatus,
                objectID: node.objectID,
                parentID: node.parentID,
                objectDescription: node.objectDescription,
                objectType : node.objectType,
                parentType : node.parentType,
                group: id
            };
        }

        function createGraphNodes(nodeGroups, nodeDevices) {
            var nodes = [];
            var id = 0;
            nodeGroups.forEach(function(node) {
                nodes.push(createGroupNode(node, id));
                ++id;
            });

            nodeDevices.forEach(function(node) {
                nodes.push(createDeviceNode(node, id));
                ++id;
            });
            return nodes;
        }

        function createGraphLinks(nodeGroups, nodes) {
            var links = [];
            var id = 0;

            nodeGroups.forEach(function(nodeGroup) {
                nodes.forEach(function(node) {
                    if (node.parentID === nodeGroup.objectID &&
                        node.parentType === nodeGroup.objectType) {
                        links.push( {
                            link_id : id,
                            source : arrayNodeIndexOf(nodes, nodeGroup),
                            target: arrayNodeIndexOf(nodes, node),
                            value : 15,
                            link_type : node.objectType,
                            state: getDeviceLinkState(node),
                        });
                        ++id;
                    }
                });

                links.push( {
                    link_id : id,
                    source : arrayNodeIndexOf(nodes, { objectID: "101", objectType: "LOCAL_GUARDIAN_DEVICE" }),
                    target: arrayNodeIndexOf(nodes, nodeGroup),
                    value : 15,
                    link_type : nodeGroup.objectType,
                    state: getGroupLinkState(nodeGroup),
                });
                ++id;
            });

            return links;
        }

        function updateGraphLinks(links, nodes) {
            var nodeDeviceTypes = guardianService.getDeviceTypes();
            var index = -1;

            links.forEach(function(link) {
                var isDeviceLink = nodeDeviceTypes.indexOf(link.link_type) !== -1;
                index = arrayNodeIndexOf(nodes, link.target);

                if (index != -1) {
                    if (isDeviceLink) {
                        link.state = getDeviceLinkState(nodes[index])
                    } else {
                        link.state = getGroupLinkState(nodes[index])
                    }
                }
            });
        }

        function updateGraphNodes(nodeGroups, nodeDevices, nodes) {
            var nodesRet = [];
            var nodeDeviceTypes = guardianService.getDeviceTypes();

            nodes.forEach(function(node) {
                var index = -1;
                var newNode = null;
                var isDevice = nodeDeviceTypes.indexOf(node.objectType) !== -1;

                if (isDevice) {
                    index = arrayNodeIndexOf(nodeDevices, node);
                } else {
                    index = arrayNodeIndexOf(nodeGroups, node);
                }

                if (index !== -1) {
                    if (isDevice) {
                        newNode = createDeviceNode(nodeDevices[index], node.group);
                    } else {
                        newNode = createGroupNode(nodeGroups[index], node.group);
                    }
                    angular.merge(node, newNode);
                    nodesRet.push(newNode);
                }
            });

            return nodesRet;
        }

        function refreshGraphInternal(nodeGroups, nodeDevices, scope, nodes) {
            scope.graph.links = createGraphLinks(nodeGroups, nodes);
            scope.cachedNodes = angular.copy(nodes);

            updateGraphNames(nodes);
            updateNetworkGraph(scope.graph);
        }

        function refreshGraph(nodeGroups, nodeDevices, scope) {
            // Create graph nodes as usual
            scope.graph.nodes = createGraphNodes(nodeGroups, nodeDevices);

            // Continue with the refresh
            refreshGraphInternal(nodeGroups, nodeDevices, scope, scope.graph.nodes);
        }

        function initializeGraphData(nodeGroups, nodeDevices, scope) {
            // Create the graph nodes from the initial data retrieved
            var nodes = createGraphNodes(nodeGroups, nodeDevices);

            // Select the default node (should be the Guardian node)
            selectDefaultNode(nodes, guardianService.localProductNodeName());
            scope.defaultNodeWasSelected = true;

            // Now we can actually assign the nodes to the scope
            scope.graph.nodes = nodes;

            // Continue with what would otherwise be a normal call to refreshGraph
            refreshGraphInternal(nodeGroups, nodeDevices, scope, nodes);
        }

        function updateGraph(nodeGroups, nodeDevices, scope) {
            scope.cachedNodes = updateGraphNodes(nodeGroups, nodeDevices, scope.graph.nodes);
            updateGraphLinks(scope.graph.links, scope.graph.nodes);
            updateNetworkGraph(scope.graph);
            updateGraphNames(scope.graph.nodes);
            cachedGraph.nodes = scope.graph.nodes;
            cachedGraph.links = scope.graph.links;
        }

        function retrieveCachedGraph() {
            return cachedGraph;
        }

        function arrayNodeIndexOf(array, node) {
            var iRet = -1;
            for (var i = 0, len = array.length; i < len; ++i) {
                if (array[i]["objectID"] === node.objectID &&
                        array[i]["objectType"] === node.objectType) {
                    iRet = i;
                }
            }

            return iRet;
        }

        function getGroupLinkState(node) {
            return (node.groupState === "Running" || node.status === "Running") ? 0 : 1;
        }

        function getDeviceLinkState(node) {
            return (node.deviceStatus === "Connected (Processing)" || node.status === "Connected (Processing)") ? 0 : 1;
        }

        function getCurrentSelectedNodeKey() {
            return currentNode.nodeKey;
        }

        function getNodeKey(device) {
            return device.objectType + ' ' + device.objectID;
        }

        function getParentNodeKey(device) {
            return device.parentType + ' ' + device.parentID;
        }

        function currentNodeIsInactive() {
            return fxAppStringService.includes(currentNode.status,'Disabled') ||
                fxAppStringService.includes(currentNode.status, 'Communications Error')
        }

        /**
         * Get the object type of the current node
         * @return {string}  The node's object type
         */
        function getCurrentSelectedNodeType() {
           return currentNode.objectType;
        }

        /**
         * Updates the list of names to be displayed in the dropdown selector.
         * 
         * @param {array} nodes Nodes to create the list from.
         */
        function updateGraphNames(nodes) {
            var names = [];

            /**
             * Inner convenience function to find the parent of a node given the current
             * list of nodes.
             * 
             * @param {object} childNode Node to find the parent node for.
             */
            function getParentNode(childNode) {

                var retNode = null;

                nodes.forEach(function(parentNode) {
                    if (parentNode.nodeKey === getParentNodeKey(childNode)) {
                        retNode = parentNode;
                    }
                });

                return retNode;
            }

            nodes.forEach(function (node) {
               
                // Parent nodes and children nodes have the same structure,
                // children just don't use the 'children' array.
                var nodeObj = {
                    id: getNodeKey(node),
                    name: node.name + ' - ' + 
                        fxAppStringService.capitalizeFirstLetter(node.objectDescription),
                    children: []
                };

                var parentNode = getParentNode(node);

                // If there's no parent node, we are a parent.
                if (!parentNode) {
                    names.push(nodeObj);
                // Otherwise, find our parent and put us into its children array.
                } else {
                    for (var existingNode in names) {
                        if (names[existingNode].id === getParentNodeKey(node)) {
                            names[existingNode].children.push(nodeObj);
                        }
                    }
                }
            });

            nodeNames = names;
        }

        /**
         * Gets text connection descriptions of the current object.
         * 
         * @return {string} A string containing connection info.
         */
        function currentConnectionInfo() {
            return Object.keys(currentNode.connections).map(function (connKey) {
                return connKey + ': ' + currentNode.connections[connKey];
            }).join('\n') + '\n';
        }
        
        //Helper function called every time a node is selected to update the node info.
        function updateCurrentSelectedNodeInfo() {
            var nodeType = getCurrentSelectedNodeType();
            var nodeInfo = "";

            var nodeKey = getCurrentSelectedNodeKey();
            if (guardianService.getDeviceTypes().includes(nodeType)) {
                var deviceInfo = "";
                if (nodeKey in deviceValueMap) {
                    var selectedDevice = deviceValueMap[nodeKey];
                    deviceInfo = 'Device IP: ' + getNodeInfoProperty(selectedDevice, 'deviceAddress') +
                                 'Serial: ' + getNodeInfoProperty(selectedDevice, 'deviceSerial') +
                                 'Product Name: ' + getCurrentSelectedNodeDescription() +
                                 'Version: ' + getNodeInfoProperty(selectedDevice, 'deviceFirmware') +
                                 'Hash: ' + getNodeInfoProperty(selectedDevice, 'deviceHash');
                        
                    // If we're a card, append the key storage checksum and features.
                    if (isCurrentSelectedNodeHSM()) {
                        deviceInfo += 'Features: ' + getNodeInfoProperty(selectedDevice, 'deviceFeatures');
                        deviceInfo += 'Key storage checksum: ' + getDeviceKeyStorageChecksum(selectedDevice) + '\n';
                    }
                }

                nodeInfo = deviceInfo;

            } else if (guardianService.getGroupTypes().includes(nodeType)) {
                var deviceGroupStr =  'Group Name: ' + currentNode.name + '\n' + currentConnectionInfo();

                // If devices group is empty will display an empty string.
                if (nodeKey in groupValueMap) {
                    var primaryDevice = getPrimaryChild(nodeKey);
                    var selectedDeviceGroup = groupValueMap[nodeKey];

                    deviceGroupStr = 'Group status: ' + getNodeInfoProperty(currentNode, "status") + '\n';

                    selectedDeviceGroup.forEach(function (deviceKey) {
                        
                        var device = deviceValueMap[deviceKey];
                        var isPrimaryDevice = (deviceKey === primaryDevice);
                        
                        function labelIfPrimary (label) {
                            return isPrimaryDevice ? label + ' (Primary Device): ' : label + ": ";
                        }
                        
                        deviceGroupStr += labelIfPrimary('Device IP') + getNodeInfoProperty(device, 'deviceAddress') +
                                          labelIfPrimary('Serial')  + getNodeInfoProperty(device, 'deviceSerial') +
                                          labelIfPrimary('Hash') + getNodeInfoProperty(device, 'deviceHash') +
                                          labelIfPrimary('Status') + getNodeInfoProperty(device, "deviceStatus") + '\n';
                    });
                }
                
                nodeInfo = deviceGroupStr;
            }
            
            currentSelectedNodeInfo = nodeInfo;
        }

        //Helper function called every time a node is selected to update the node img src.
        function updateCurrentSelectedNodeImgSrc() {
            var nodeType = getCurrentSelectedNodeType();
            var productImg = "/guardian/static/images/";

            if (guardianService.getDeviceTypes().includes(nodeType)) {
                if (nodeType == 'CARD') {
                    productImg += 'vectera-plus';
                } else if (nodeType == 'KMES_DEVICE') {
                    productImg += 'kmes-3';
                } else if (nodeType == "REMOTE_KEY_DEVICE") {
                    productImg += 'rkms-3';
                } else if (nodeType == 'LOCAL_GUARDIAN_DEVICE') {
                    productImg += 'guardian-3';
                }
            } else if (guardianService.getGroupTypes().includes(nodeType)) {
                productImg += "device-stack";
            }

            if (currentNodeIsInactive()) {
                productImg += "-question-mark";
            }
            productImg += ".png";

            currentSelectedNodeImgSrc = productImg;
        }

        function setCurrentSelectedNode(nextNode) {
            currentNode = nextNode;
            updateCurrentSelectedNodeInfo();
            updateCurrentSelectedNodeImgSrc();
        }

        function getCurrentSelectedNodeImgSrc() {
            return currentSelectedNodeImgSrc;
        }

        function getCurrentSelectedNodeInfo() {
            return currentSelectedNodeInfo;
        }

        function checkStat(objectData) {
            return objectData.objectType === 'AGGREGATE_STAT' ||
                   objectData.objectType === 'INDIVIDUAL_STAT';
        }

        function isBalancerStat(objectData) {
            return objectData.name === 'Balancer Connection Sum' ||
                   objectData.name === 'Balancer Open Connection Count';
        }

        function getBalancerStatName(objectData) {
            return objectData.name;
        }

        function getEpoch() {
            return fxAppViewService.ISOTimetoFXTime(new Date(0).toISOString());
        }

        function getNow() {
            return fxAppViewService.ISOTimetoFXTime(new Date().toISOString());
        }

        function dateGTENow(candidate) {
            var todayMoment = moment(new Date());
            var candidateMoment = moment(candidate);

            return todayMoment.date() === candidateMoment.date() ||
                candidateMoment.isAfter(todayMoment, 'day');
        }

        function dateGTNow(candidate) {
            var todayMoment = moment(new Date());
            var candidateMoment = moment(candidate);

            return candidateMoment.isAfter(todayMoment, 'day');
        }

        /**
         * Checks if the period from begin to end is live
         * @param period the period to check
         * @return if the current time in within the period
         */
        function checkPeriodIsLive(period) {
            return dateGTENow(period.end) &&
                   !dateGTNow(period.begin);
        }

        function checkIsLive(statSelectedDate) {
            var result = {};

            Object.keys(statSelectedDate).map(function(chartName) {
                result[chartName] = checkPeriodIsLive(statSelectedDate[chartName]);
            });

            return result;
        }

        function diffDays(baseDate, daysDiff) {
            return moment(baseDate).add(daysDiff, 'days').toDate();
        }

        // Get the date representing the start of the current day (first second)
        function startOfDay() {
            var date = new Date();
            date.setHours(0, 0, 0, 0);
            return date;
        }

        // Get the date representing the end of the current day (last second)
        function endOfDay() {
            var date = new Date();
            date.setHours(23, 59, 59, 999);
            return date;
        }

        function greaterThanDiffMS(greaterThanCandidate, lessThanCandidate, diffMS) {
            return greaterThanCandidate > (lessThanCandidate + diffMS);
        }

        function checkTimeSinceChartLastChecked(chartLastChecked) {
            var delayMs = 5000;
            var nowMs = new Date().getTime();
            var chartLastCheckedMs = new Date(chartLastChecked).getTime();

            return greaterThanDiffMS(nowMs, chartLastCheckedMs, delayMs);
        }

        function iterStatChartNames(statCharts, callback) {
            statCharts.forEach(function(chartName) {
                callback(chartName);
            });
        }

        function clearStatMapByTypeAndGroup(typeName, groupName, statMap) {
            statMap[typeName][groupName] = [];
        }

        /**
         * Calculate accessory data for an individual stat
         * @param stat the stat object
         * @param accessoryData the accessory data
         * @return the accessory data as an object
         */
        function statAccessoryData(objectData, accessoryData) {
            var statType = objectData.status
            if (statType === 'Balancer Open Connection Count') {
                return {
                    connectionCount: accessoryData[0],
                    groupID: accessoryData[1],
                    groupName: accessoryData[2]
                };
            } else if (statType === 'Command Statistics') {
                return {
                    command: accessoryData[0],
                    requestText: accessoryData[1],
                    responseText: accessoryData[2],
                    deviceGroupName: accessoryData[3],
                    deviceName: accessoryData[4],
                    errorMessage: accessoryData[5],
                    success: accessoryData[6],
                    rtt: accessoryData[7],
                    deviceLatency: accessoryData[8],
                    guardianLatency: accessoryData[9],
                };
            } else {
                return {};
            }
        }

        function getStatData(objectData, managerType) {
            var statData = {};

            if (managerType === 'AGGREGATE_STAT') {
                var accessoryData = JSON.parse(objectData.accessoryData);

                if (accessoryData) {
                    statData = {
                        groupName: accessoryData.group_name,
                        aggTime: objectData.aggregationEndTime,
                        connectionCount: accessoryData.connections_opened
                    };
                }
            }
            else if (managerType === 'INDIVIDUAL_STAT') {
                var accessoryData = [];
                if (objectData.data) {
                    accessoryData = objectData.data.split(',');
                }

                if (accessoryData.length) {
                    statData = Object.assign({
                        // Convert entry time to millisecond format for the graph
                        entryTime: new Date(objectData.entryTime).getTime(),
                    }, statAccessoryData(objectData, accessoryData));
                }
            }

            return statData;
        }

        function updateStatMap(objectData, statMap, statName, managerType) {
            var statData = getStatData(objectData, managerType);

            if (statData.groupName && checkStatGroupName(statData.groupName)) {
                updateStatNameInStatMap(statData, objectData, statMap, statName);
            }
        }

        function updateStatNameInStatMap(statData, objectData, statMap, statName) {
            var maxSeriesLength = 100;

            // Get the stat data for the group
            var groupStatData = statMap[statName][statData.groupName];

            // Initialize the stat data if needed
            if (!groupStatData) {
                groupStatData = [];
            }

            // Ensure the maximum series length is not exceeded
            if (groupStatData.length >= maxSeriesLength) {
                groupStatData.shift();
            }

            // Update the stat data for the group in the stat map
            groupStatData.push(statData);
            statMap[statName][statData.groupName] = groupStatData;
        }

        function checkStatGroupName(group_name) {
            var guardianDeviceType = guardianService.defaultGuardianGroup().childType;
            var guardianDeviceGroupName = guardianService.getGroupType(guardianDeviceType);

            var groupNameExistsInNodes = cachedGraph.nodes.filter(function (node) {
                return group_name === node.groupName;
            }).length > 0;

            return groupNameExistsInNodes || group_name === guardianDeviceGroupName;
        }

        function addAggStatGroupNameClause(clauses, groupName, operator) {
            clauses.push({
                objectType: "aggregate statistic",
                presentationType: "Balancer Connection Sum",
                field: "group name",
                operator: operator,
                match: "EXACT",
                value: groupName,
                minValue: "",
                maxValue: ""
            });
        }

        function addIndStatGroupNameClause(clauses, statName, groupName, operator) {
            var groupNameField = "group name";
            if (statName === "Command Statistics") {
              groupNameField = "device group name";
            }

            clauses.push({
                objectType: "individual statistic",
                presentationType: statName,
                field: groupNameField,
                operator: operator,
                match: "EXACT",
                value: groupName,
                minValue: "",
                maxValue: ""
            });
        }

        function sortStatDataByDate(data) {
            var convertDate = function (entry) {
                return new Date(entry.entryTime).getTime();
            }

            // Sort occurs in-place (does not return a copy)
            // Ensure the most recent stat is last
            data.sort(function(a, b) {
                var aSeconds = convertDate(a);
                var bSeconds = convertDate(b);
                return aSeconds - bSeconds;
            });
        }

        function retrieveStatsRequest(filter, managerType, moreData) {
            var deferred = $q.defer();

            // Make the request
            $http.post(window.apipath('/object'), filter).success(function(data) {
                var logFilter = data.objectData['LOG_FILTER'];
                var logFilterJson = logFilter ? JSON.parse(logFilter) : null;
                var numChunks = logFilterJson ? logFilterJson.chunkCount : 0;
                var chunk = logFilterJson ? logFilterJson.chunk : 0;
                var matchCount = logFilterJson ? logFilterJson.matchCount : 0;

                var parsedData = data.objectData[managerType].map(function(item) {
                    return JSON.parse(item);
                });

                // Sort balancer open connection counts by descending date
                if (managerType === 'INDIVIDUAL_STAT') {
                    sortStatDataByDate(parsedData);
                }

                deferred.resolve(Object.assign({
                    data: parsedData,
                    numChunks: numChunks,
                    chunk: chunk,
                    matchCount: matchCount,
                    result: data.result,
                    error: data.error || '',
                }, moreData));
            });

            return deferred.promise;
        }

        /**
         * Build filter results for statistics
         * @param managerType the manager type
         * @return the filter request data
         */
        function statsRequestData(managerType) {
            return filterService.requestData(managerType, 'RESULTS', {}, []);
        }

        function statsOrdering(managerType, index, reverseAscending) {
            var sortColumn = "entry_time";
            if (managerType === "AGGREGATE_STAT") {
                // This is scheduled to be refactored
                sortColumn = "agg_begin_time";
            }

            var ascending = false;
            if (reverseAscending) {
              ascending = true;
            }
            return filterService.orderingData(100, index, sortColumn, ascending);
        }

        function statsClauses(minDate, maxDate, managerType, statName, groupName) {
            clauses = []

            // Build the clauses
            if (managerType === "AGGREGATE_STAT") {
                clauses = [{
                    objectType: "aggregate statistic",
                    field: "aggregation end",
                    operator: "AND",
                    match: "DATE_DELTA_RANGE",
                    value: "",
                    minValue: minDate ? minDate : getEpoch(),
                    maxValue: maxDate ? maxDate : getNow()
                }];

                // Determine the group name clauses
                if (!groupName) {
                    // No group name specified, so query for all
                    guardianService.getGroupTypes().map(function(groupName) {
                        addAggStatGroupNameClause(clauses, groupName, "OR");
                    });
                }
                else {
                    // Group name was specified
                    addAggStatGroupNameClause(clauses, groupName, "AND");
                }
            }
            else if (managerType.startsWith("INDIVIDUAL_STAT")) {
                clauses = [{
                    objectType: "individual statistic",
                    field: "entry time",
                    operator: "AND",
                    match: "DATE_DELTA_RANGE",
                    value: "",
                    minValue: minDate ? minDate : getEpoch(),
                    maxValue: maxDate ? maxDate : getNow()
                }, {
                    objectType: "individual statistic",
                    field: "status",
                    operator: "AND",
                    match: "EXACT",
                    value: statName,
                    minValue: '',
                    maxValue: ''
                }];

                // Determine the group name clauses
                addIndStatGroupNameClause(clauses, statName, groupName ? groupName : '', "AND");
            }

            return clauses;
        }

        function getStatFilter(minDate, maxDate, managerType, statName, groupName, index, reverseAscending) {
            // Gather the filter parameters
            var request = statsRequestData(managerType);
            var ordering = statsOrdering(managerType, index, reverseAscending);
            var clauses = statsClauses(minDate, maxDate, managerType, statName, groupName);

            return filterService.makeFilter(request, ordering, clauses);
        }

        function retrieveStats(minDate, maxDate, managerType, statName, groupName, index) {
            var deferred = $q.defer();

            var filter = getStatFilter(minDate, maxDate, managerType, statName, groupName, index, false);

            // Get the total number of chunks available
            retrieveStatsRequest(filter, managerType).then(function(results) {
                var numChunks = results.numChunks;

                // Ensure a valid index exists
                index = index ? index : 0;

                // Make a filter query with the new index
                var filter = getStatFilter(minDate, maxDate, managerType, statName, groupName, index, false);

                // Make the request
                retrieveStatsRequest(filter, managerType).then(function(results) {
                    deferred.resolve(results);
                });
            });

            return deferred.promise;
        }

        // Same as retrieveStats by filter
        function getStatChunk(filter, moreData) {
            return retrieveStatsRequest(filter, filter.request.manager, moreData);
        }

        function updateStatChart(seriesName, seriesData, chartData, keyNameX, keyNameY, transformationFunc, pagination, period) {
            if (seriesName) {
                // Get the series from the series data using the name specified
                var foundSeries = findSeries(chartData, seriesName);

                var transformedSeries = seriesData;
                if (transformationFunc) {
                    transformedSeries = transformationFunc(seriesData, pagination, period);
                }

                // Populate the series with values
                if (foundSeries) {
                    foundSeries.values = mapSeriesData(transformedSeries, keyNameX, keyNameY);
                }
            }
        }

        function findSeries(chartData, key) {
            return chartData.filter(function(series) {
                return series.key === key || series.originalKey === key;
            })[0];
        }

        function mapSeriesData(seriesData, keyNameX, keyNameY) {
            return seriesData.map(function(point) {
                return {
                    x: point[keyNameX],
                    y: point[keyNameY]
                };
            });
        }

        function nvd3DataNameFromChartName(chartName) {
            var dataName = '';

            switch(chartName) {
                case 'connChart':
                    dataName = 'connData';
                    break;
                case 'currConnChart':
                    dataName = 'currConnData';
                    break;
                default:
                    break;
            }

            return dataName;
        }

        function statNameFromChartName(chartName) {
            var statName = '';

            switch(chartName) {
                case 'connChart':
                    statName = 'Balancer Connection Sum';
                    break;
                case 'currConnChart':
                    statName = 'Balancer Open Connection Count';
                    break;
                default:
                    break;
            }

            return statName;
        }

        function managerTypeFromChartName(chartName) {
            var managerType = '';

            switch(chartName) {
                case 'connChart':
                    managerType = 'AGGREGATE_STAT';
                    break;
                case 'currConnChart':
                    managerType = 'INDIVIDUAL_STAT';
                    break;
                default:
                    break;
            }

            return managerType;
        }

        /**
         * Convert returned connection count data to make the graph more readable.
         * If on the first page, add the current time to the end of the data with the current count.
         * If on the last page, add the start of the time window with count of 0.
         * @param data the data to transform.
         * @param pagination the data about the current pagination.
         * @param period the window of time the data covers.
         * @return the transformed data.
         */
        function transformConnectionCount(data, pagination, period) {
            if (data.length <= 0) {
                return data;
            }

            var isLive = checkPeriodIsLive(period);
            var firstPage = pagination.currentPage === 1;
            var lastPage = pagination.currentPage === pagination.totalPages;

            var lastVal = data[data.length - 1];

            // Extend the last recorded stat to the current time
            if (firstPage && isLive) {
                var entryCurrentTime = Object.assign({}, lastVal)
                entryCurrentTime.entryTime = new Date().getTime();
                data.push(entryCurrentTime);
            }

            // Add 0 for the first time in the window
            if (lastPage) {
                var entryStartTime = Object.assign({}, lastVal)
                entryStartTime.entryTime = new Date(period.begin).getTime();
                entryStartTime.connectionCount = "0";
                data.unshift(entryStartTime);
            }

            return data;
        }

        function chartSeriesParamsFromChartName(chartName) {
            var chartSeriesParams = {};

            switch(chartName) {
                case 'connChart':
                    chartSeriesParams = {
                        seriesName: 'Connection Count',
                        keyNameX: 'aggTime',
                        keyNameY: 'connectionCount'
                    };
                    break;
                case 'currConnChart':
                    chartSeriesParams = {
                        seriesName: 'Connection Count',
                        keyNameX: 'entryTime',
                        keyNameY: 'connectionCount',
                        transformationFunc: transformConnectionCount,
                    };
                    break;
                default:
                    break;
            }

            return chartSeriesParams;
        }

        function selectDefaultNode(nodes, nodeName) {
            // Find the index of the default node
            var defaultNodeIndex = nodes.findIndex(function(node) {
                return node.name.search(nodeName) !== -1;
            });

            if (defaultNodeIndex >= 0) {
                // Get a reference to the default node
                var defaultNode = nodes[defaultNodeIndex];

                // Take it from where it currently is...
                nodes.splice(defaultNodeIndex, 1);

                // Make it the first node in the list
                nodes.splice(0, 0, defaultNode);

                // Select the default node
                $window.setNodeSelection(defaultNode);
            }
        }

        function redrawGraph(graph) {
            updateAndRedrawGraph(graph);
        }

        /**
         * Update the graph without redrawing it
         * @param {object}  graph  The graph representation
         */
        function updateGraphNoRedraw(graph) {
            updateGraphInternal(graph);
        }

        function nextPage(pagination, chartName) {
            var chartPageState = pagination[chartName];
            var canGoToNext = chartPageState.currentPage < chartPageState.totalPages;

            if (canGoToNext) {
                chartPageState.currentPage++;
            }

            return canGoToNext;
        }

        function prevPage(pagination, chartName) {
            var chartPageState = pagination[chartName];
            var canGoToPrev = chartPageState.currentPage > 1;

            if (canGoToPrev) {
                chartPageState.currentPage--;
            }

            return canGoToPrev;
        }

        /**
         * Return the currently selected node name
         * @return {string}  The current node name
         */
        function getCurrentSelectedNodeName() {
            return currentNode.name;
        }

        /**
         * Get the group name used to query for stats based on the selected node
         * @return {string}  The current node name
         */
        function getCurrentSelectedNodeDeviceGroupName() {
            var deviceGroupName = currentNode.groupName;

            // Use the local guardian group when that node is selected
            var guardianDeviceType = guardianService.defaultGuardianGroup().childType;
            if (currentNode.objectType === guardianDeviceType) {
                deviceGroupName = guardianService.getGroupType(guardianDeviceType);
            }

            // Use the parent group name when a device is selected
            else if (!currentNode.groupName) {
                // Try to find parent node
                var nodesFound = cachedGraph.nodes.filter(function(node) {
                    return node.objectID === currentNode.parentID;
                });

                // Get the group name from the parent node if one was found
                if (nodesFound.length) {
                    var parentNode = nodesFound[0];
                    deviceGroupName = parentNode.groupName ? parentNode.groupName : '';
                }
            }

            return deviceGroupName;
        }

        /**
         * Safe way to retrieve a property of a node object.
         * 
         * @param {object} node Device or group node.
         * @param {string} infoProperty Some property of the node.
         * 
         * @return {string} Property of the node, or "N/A" if it doesn't exist.
         */
        function getNodeInfoProperty(node, infoProperty) {
            return (node[infoProperty] ? node[infoProperty] : "N/A") + '\n';
        }
       
        /**
         * Gets the key storage checksum for the given device node.
         * 
         * @param {object} device Device node (HSM device).
         * 
         * @return {string} Key storage checksum, or "N/A" on failure.
         */
        function getDeviceKeyStorageChecksum(device) {
            var hashArr = getNodeInfoProperty(device, 'deviceHash').split(",");

            // There should be four, but...
            if (hashArr.length >= 2) {
                return hashArr[1];
            }

            return "N/A";
        }

        /**
         * Checks if the currently selected node is an HSM.
         * 
         * @return {bool} True if the current node is an HSM, false otherwise.
         */
        function isCurrentSelectedNodeHSM() {
            return (guardianService.getGroupType(getCurrentSelectedNodeType()).indexOf("CARD") >= 0);
        }

        /**
         * Return the current selected group type (parent type for devices and object type for groups)
         * @return {string}  The current group type
         */
        function getCurrentSelectedNodeGroupType() {
            return guardianService.getGroupType(getCurrentSelectedNodeType());
        }

        /**
         * Get the object type in a human readable form
         * @return {string}  The selected object's description
         */
        function getCurrentSelectedNodeDescription() {
            return fxAppStringService.capitalizeFirstLetter(currentNode.objectDescription || 'Local Guardian Device') + '\n';
        }

        function getNodeNames() {
            return nodeNames;
        }

        function getNodeByKey(nodeKey) {
            return cachedGraph.nodes.filter(function (node) {
                return nodeKey === getNodeKey(node);
            })[0];
        }


        /**
         * Get the primary child node of a given group
         * @param {string}  nodeKey  The group device
         * @return {string}  The primary child key or null if none exists
         */
        function getPrimaryChild(nodeKey) {
            var groupChildren = null;
            if (nodeKey in groupValueMap) {
                groupChildren = groupValueMap[nodeKey];
            }

            var childKey = null;
            if (groupChildren && groupChildren.length) {
                childKey = groupChildren.reduce(function (selectedKey, currentKey) {
                    var currentChild = deviceValueMap[currentKey];
                    return guardianService.isPrimaryDevice(currentChild) ? currentKey : selectedKey;
                });
            }

            return childKey;
        }

        return {
            manageNodeViewContentLayout: manageNodeViewContentLayout,
            deviceValueMap: deviceValueMap,
            groupValueMap: groupValueMap,
            getGroupTypes: guardianService.getGroupTypes,
            getDeviceTypes: guardianService.getDeviceTypes,
            isDeviceType: guardianService.isDeviceType,
            isGroupType: guardianService.isGroupType,
            getDeviceGroups: getDeviceGroups,
            getDevices: getDevices,
            refreshGraph: refreshGraph,
            initializeGraphData: initializeGraphData,
            updateGraph: updateGraph,
            updateGraphNoRedraw: updateGraphNoRedraw,
            arrayNodeIndexOf: arrayNodeIndexOf,
            createDeviceNode: createDeviceNode,
            createGroupNode: createGroupNode,
            getCurrentSelectedNodeKey: getCurrentSelectedNodeKey,
            getCurrentSelectedNodeDescription: getCurrentSelectedNodeDescription,
            getNodeKey: getNodeKey,
            getParentNodeKey: getParentNodeKey,
            getCurrentSelectedNodeType: getCurrentSelectedNodeType,
            getCurrentSelectedNodeName: getCurrentSelectedNodeName,
            getCurrentSelectedNodeGroupType: getCurrentSelectedNodeGroupType,
            getCurrentSelectedNodeDeviceGroupName: getCurrentSelectedNodeDeviceGroupName,
            getNodeByKey: getNodeByKey,
            getNodeNames: getNodeNames,
            getPrimaryChild: getPrimaryChild,
            setCurrentSelectedNode : setCurrentSelectedNode,
            getCurrentSelectedNodeImgSrc: getCurrentSelectedNodeImgSrc,
            getCurrentSelectedNodeInfo: getCurrentSelectedNodeInfo,
            ISOTimetoFXTime: fxAppViewService.ISOTimetoFXTime,
            checkStat: checkStat,
            isBalancerStat: isBalancerStat,
            getBalancerStatName: getBalancerStatName,
            checkIsLive: checkIsLive,
            diffDays: diffDays,
            startOfDay: startOfDay,
            endOfDay: endOfDay,
            greaterThanDiffMS: greaterThanDiffMS,
            checkTimeSinceChartLastChecked: checkTimeSinceChartLastChecked,
            nvd3DataNameFromChartName: nvd3DataNameFromChartName,
            iterStatChartNames: iterStatChartNames,
            updateStatMap: updateStatMap,
            getStatData: getStatData,
            retrieveStats: retrieveStats,
            getStatChunk: getStatChunk,
            statsRequestData: statsRequestData,
            statsOrdering: statsOrdering,
            statsClauses: statsClauses,
            updateStatChart: updateStatChart,
            clearStatMapByTypeAndGroup: clearStatMapByTypeAndGroup,
            statNameFromChartName: statNameFromChartName,
            managerTypeFromChartName: managerTypeFromChartName,
            chartSeriesParamsFromChartName: chartSeriesParamsFromChartName,
            selectDefaultNode: selectDefaultNode,
            retrieveCachedGraph: retrieveCachedGraph,
            redrawGraph: redrawGraph,
            nextPage: nextPage,
            prevPage: prevPage
        };
    }]
);

