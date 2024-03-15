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
fxApp.factory('nodeStatBoxService',
    ['guardianService', 'nodeViewService', 'chartFactory',
    function (guardianService, nodeViewService, chartFactory) {

    var statTypes = ['tps', 'cpu', 'mem', 'temp'];

    // The json name in the managed object
    var statTypeToJson = {
        tps: 'statTPS',
        cpu: 'statCPUUsage',
        mem: 'statDeviceMemory',
        temp: 'statCaseTemperature'
    };

    // Display data
    var statBoxProperties = {
        tps:  {key: 'TPS',    title: 'TPS Rate',  icon: 'exchange'},
        cpu:  {key: 'CPU',    title: 'CPU',       icon: 'percent'},
        mem:  {key: 'Memory', title: 'Memory',    icon: 'percent'},
        temp: {key: 'Case',   title: 'Case Temp', icon: 'fire'}
    };

    var statBoxGraphData = {
        tps:  {range: [0, 10000], label: 'Transactions/sec', expandedLabel: 'Transactions/sec'},
        cpu:  {range: [0, 100],   label: '% Usage',          expandedLabel: 'CPU % Usage'},
        mem:  {range: [0, 100],   label: '% Usage',          expandedLabel: 'Memory % Usage'},
        temp: {range: [0, 100],   label: 'Temp. (F)',        expandedLabel: 'Case Temperature(F)'}
    }

    // Cached device and group data
    var cachedStatData = {};

    var statData = {
        tps: makeData('tps', []),
        cpu: makeData('cpu', []),
        mem: makeData('mem', []),
        temp: makeData('temp', [])
    };

    /**
     * Get properties for the stat graphs
     */
    function getStatProperties(statType) {
        return angular.copy(statBoxProperties[statType]);
    }

    /**
     * Make a device mapping for a statistics view
     */
    function makeDeviceStatMap() {
        return {tps: [], cpu: [], mem: [], temp: []};
    }

    /**
     * Make the chart options for the stat box
     * @param {string}  statType  The type of stat to make a graph for
     * @param {boolean}  height  Graph height for taller graphs
     */
    function makeOptions(statType, height) {
        var graphData = statBoxGraphData[statType];
        return chartFactory.lineChart({
            chartTitle: '',
            xAxisLabel: 'Time(s)',
            yAxisLabel: graphData.expandedLabel,
            xDomain: [0, 90],
            yDomain: graphData.range,
            height: height,
        });
    }

    /**
     * Create the graph data structure
     */
    function makeData(statType, values) {
        return [{
            key: statBoxProperties[statType].key,
            values: values ? values : []
        }];
    }

    /**
     * Get cached data or if it doesn't exist create it
     * @param {string}  nodeKey  The node specific key mapping
     * @return {object}  The cached data
     */
    function getCachedData(nodeKey) {
        if ((nodeKey in cachedStatData) === false) {
            cachedStatData[nodeKey] = makeDeviceStatMap();
        }

        return cachedStatData[nodeKey];
    }

    /**
     * Update the stat cache on object change
     * @param {string}  nodeKey  The node specific key to set as the next data
     */
    function setDataFromKey(nodeKey) {
        var nextData = getCachedData(nodeKey);
        statTypes.forEach(function (statType) {
            statData[statType][0].values = nextData[statType];
        });
    }

    /**
     * Update a stat graph for a device or group with the new values
     * @param {number}  value  The new values
     * @param {array}  values  The list of current values
     */
    function updateStatGraph(value, values) {
        var dataLength = values.length;

        if (dataLength <= 90) {
            values.push({ 'x': dataLength, 'y' : value });
        } else {
            for (var i = 0; i < (dataLength-1); i++) {
                values[i].x = i;
                values[i].y = values[i+1].y;
            }
            values[dataLength-1].x = dataLength-1;
            values[dataLength-1].y = value;
        }
    }

    /**
     * Function for updating the statistics object when socket:update_object is triggered
     */
    function updateStatObject(ev, data) {
        var objectData = data.objectData;
        var objectType = objectData.objectType;
        if (!nodeViewService.isDeviceType(objectType)) {
            return;
        }

        var deviceData = null;
        var nodeKey = nodeViewService.getNodeKey(objectData);

        // Get or create current device entry
        deviceData = getCachedData(nodeKey);

        // Update stats in device entry
        statTypes.forEach(function (statType) {
            updateStatGraph(objectData[statTypeToJson[statType]], deviceData[statType]);
        });

        // Assign display variables to device entry
        if (nodeKey === nodeViewService.getCurrentSelectedNodeKey() && deviceData !== null) {

            statTypes.forEach(function (statType) {
                statData[statType][0].values = deviceData[statType];
            });
        }
    };

    // The function to call to unbind the scope watch when the view changes
    var unsetUpdateObjectWatch = null;

    /**
     * Set a watcher for update_object if it doesn't exist
     * @param {function}  nextUnsetWatch  The next unset watch function
     */
    function setWatch(nextUnsetWatch) {
        if (unsetUpdateObjectWatch === null) {
            unsetUpdateObjectWatch = nextUnsetWatch;
        } else {
            // If a watch already exists deregister the given one
            nextUnsetWatch();
        }
    }

    /**
     * Remove listener for object update
     */
    function unsetWatch() {
        if (unsetUpdateObjectWatch !== null) {
            unsetUpdateObjectWatch();
            unsetUpdateObjectWatch = null;
        }
    }

    return {
        getStatProperties: getStatProperties,
        makeOptions: makeOptions,
        makeData: makeData,
        statData: statData,
        setWatch: setWatch,
        setDataFromKey: setDataFromKey,
        unsetWatch: unsetWatch,
        updateStatObject: updateStatObject
    };
}]);
