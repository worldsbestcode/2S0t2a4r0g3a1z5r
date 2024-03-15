/**
 * The base HTML of the Nodes view
 */
fxApp.component('nodeView', {
    templateUrl: 'components/sections/nodeView/content.html'
});

fxApp.factory('chartFactory', function() {
    return {
        lineChart: function(options) {
            return {
                chart: {
                    type: 'lineChart',
                    height: options.height || 100,
                    margin : {
                        top: 20,
                        right: 20,
                        bottom: 40,
                        left: 55
                    },
                    x: function(d){ return d.x; },
                    y: function(d){ return d.y; },
                    useInteractiveGuideline: true,
                    showLegend: false,
                    xAxis: {
                        axisLabel: options.xAxisLabel,
                        tickFormat: options.xAxisTickFormat,
                        staggerLabels: options.xAxisStaggerLabels,
                        axisLabelDistance: options.xAxisLabelDistance,
                    },
                    yAxis: {
                        axisLabel: options.yAxisLabel,
                        axisLabelDistance: -10,
                        domain : [ 0, 100]
                    },
                    yDomain : options.yDomain,
                    xDomain : options.xDomain,
                    interpolate : options.interpolate || 'linear',
                    margin: options.margin,
                },
                title: {
                    enable: (options.chartTitle.length > 0),
                    text: options.chartTitle
                },
                subtitle: {
                    enable: false
                },
                caption: {
                    enable: false
                }
            };
        },
        linePlusBarChart: function(options) {
            return {
                chart: {
                    type: 'linePlusBarChart',
                    height: options.height,
                    margin: {
                        top: 20,
                        right: 100,
                        bottom: 40,
                        left: 100
                    },
                    x: options.xGetter,
                    y: options.yGetter,
                    bars: {
                        forceY: [0]
                    },
                    bars2: {
                        forceY: [0]
                    },
                    color: [
                        options.barColor,
                        options.lineColor,
                    ],
                    xAxis: {
                        axisLabel: options.xAxisLabel,
                        tickFormat: options.xAxisTickFormat,
                        showMaxMin: false
                    },
                    x2Axis: {
                        tickFormat: options.xAxisTickFormat,
                        showMaxMin: false
                    },
                    y1Axis: {
                        axisLabel: options.y1AxisLabel,
                        tickFormat: options.y1AxisTickFormat,
                        axisLabelDistance: 30
                    },
                    y2Axis: {
                        axisLabel: options.y2AxisLabel,
                        tickFormat: options.y2AxisTickFormat,
                        axisLabelDistance: 20
                    }
                },
                title: {
                    enable: (options.chartTitle.length > 0),
                    text: options.chartTitle
                }
            };
        },
        multiBarChart: function(options) {
            return {
                chart: {
                    type: 'multiBarChart',
                    height: options.height,
                    margin: {
                        top: 20,
                        right: 100,
                        bottom: 40,
                        left: 100
                    },
                    color: options.colors,
                    showControls: false,
                    showLegend: false,
                    legend: {
                        radioButtonMode: true,
                        updateState: true
                    },
                    x: options.xGetter,
                    y: options.yGetter,
                    stacked: false,
                    grouped: true,
                    xAxis: {
                        axisLabel: options.xAxisLabel,
                        tickFormat: options.xAxisTickFormat,
                        showMaxMin: false,
                    },
                    yAxis: {
                        axisLabel: options.yAxisLabel,
                        tickFormat: options.yAxisTickFormat,
                        axisLabelDistance: 30
                    },
                    title: {
                        enable: (options.chartTitle.length > 0),
                        text: options.chartTitle
                    }
                }
            }
        }
    };
});

/**
 * Component that creates stats for various device statistics like TPS, CPU, Memory, Case temp
 */
fxApp.component('nodeStats', {
    templateUrl: 'components/sections/nodeView/nodeStats.html',
});

fxApp.controller('nodeStatModalCtrl', ['$scope', function($scope) {
    $scope.cancel = function () {
        $scope.$dismiss('cancel');
    };
}]);

/**
 * Node Graph Directive to build graph view widget
 */
fxApp.directive('nodeGraph', ['nodeViewService', 'guardianService', 'fxSpinnerService', function(nodeViewService, guardianService, fxSpinnerService) {
    return {
        templateUrl: 'components/sections/nodeView/nodeGraph.html',
        restrict: 'E',
        link: function(scope, element, attrs) {
            scope.currentNodeCallBack = function(currentNode) {
                scope.nodeViewService.setCurrentSelectedNode(currentNode);
            }

            initGraph(scope.currentNodeCallBack);

            // Use a persistent copy of the graph
            scope.graph = nodeViewService.retrieveCachedGraph();
            if (scope.graph["nodes"].length) {
                //If there are cached nodes don't show the spinner
                 fxSpinnerService.remove('nodeViewSpinner');
            }

            scope.defaultNodeWasSelected = false;
            scope.cachedNodes = null;

            scope.nodeViewService.getDeviceGroups().then(function(groups) {
                scope.nodeViewService.getDevices().then(function(devices) {
                    scope.nodeViewService.initializeGraphData(groups, devices, scope);

                    /* Once the node graph has loaded hide the spinner*/
                    if (fxSpinnerService.isRegistered('nodeViewSpinner')) {
                        fxSpinnerService.remove('nodeViewSpinner');
                    }
                });

            });

            // Make directive aware of conditional rendering
            scope.$emit('domReady');
        },
        controller: ['$scope', '$element', 'nodeViewService', 'socketio', function($scope, $element, nodeViewService, socketio) {
            $scope.nodeViewService = nodeViewService;

            $scope.$on('socket:delete_object', function(ev, data) {
                var objectData = data.objectData;
                var objectType = objectData.objectType;
                if (!nodeViewService.isDeviceType(objectType) && !nodeViewService.isGroupType(objectType)) {
                    return;
                }

                socketioDeleteGraphNodes(objectData);
            });

            $scope.$on('socket:update_object', function(ev, data) {
                var objectData = data.objectData;
                var objectType = objectData.objectType;
                if (!nodeViewService.isDeviceType(objectType) && !nodeViewService.isGroupType(objectType)) {
                    return;
                }

                socketioUpdateGraphNodes(objectData);

                // Select the default node if it hasn't been done already
                if (!$scope.defaultNodeWasSelected) {
                    nodeViewService.selectDefaultNode($scope.graph.nodes, guardianService.localProductName());
                    $scope.defaultNodeWasSelected = true;
                }
            });

            $scope.$on('domReady', function() {
                // Redraw graph if/when needed
                if ($scope.graph.nodes.length > 0) {
                    $scope.nodeViewService.redrawGraph($scope.graph);
                }
            });

            function socketioUpdateGraphNodes(objectData) {
                if ($scope.cachedNodes === null) {
                    return;
                }

                var deviceTypes = $scope.nodeViewService.getDeviceTypes();
                var isDevice = deviceTypes.indexOf(objectData.objectType) != -1;
                var index = $scope.nodeViewService.arrayNodeIndexOf($scope.cachedNodes, objectData);
                var updateGraph = false;
                var statusUpdate = false;

                if ((isDevice && objectData.application === false) ||     // If it's not an app card
                    (!isDevice && objectData.objectID > 1)) {             // or not the guardian group

                    if (index >= 0) {
                        var nodeTest = null;
                        if (isDevice) {
                            nodeTest = $scope.nodeViewService.createDeviceNode(objectData, $scope.cachedNodes[index].group);
                        } else {
                            nodeTest = $scope.nodeViewService.createGroupNode(objectData, $scope.cachedNodes[index].group);
                        }

                        statusUpdate = $scope.cachedNodes[index] !== nodeTest.status;

                        // Don't update full graph for connection status updates
                        $scope.cachedNodes[index].status = nodeTest.status;
                        $scope.graph.nodes[index].status = nodeTest.status;

                        updateGraph = !angular.equals(nodeTest, $scope.cachedNodes[index]);
                    } else if (index === -1) {
                        updateGraph = true;
                    }
                }

                if (updateGraph) {
                    $scope.nodeViewService.getDeviceGroups().then(function(groups) {
                        $scope.nodeViewService.getDevices().then(function(devices) {
                            if (index !== -1) {
                                $scope.nodeViewService.updateGraph(groups, devices, $scope);
                            } else {
                                $scope.nodeViewService.refreshGraph(groups, devices, $scope);
                            }

                        });
                    });
                } else if (statusUpdate) {
                    $scope.nodeViewService.updateGraphNoRedraw($scope.graph);
                }
            }

            function socketioDeleteGraphNodes(objectData) {
                var index = $scope.nodeViewService.arrayNodeIndexOf($scope.cachedNodes, objectData);

                if (index != -1) {
                    $scope.nodeViewService.getDeviceGroups().then(function(groups) {
                        $scope.nodeViewService.getDevices().then(function(devices) {
                            $scope.nodeViewService.refreshGraph(groups, devices, $scope);
                        });

                    });
                }
            }
        }]
    };

}]);

/**
 * The Nodes view controller
 */
var nodeViewCtrl = fxApp.controller('nodeViewCtrl',
	['$scope', '$rootScope', '$http', 'fxAppService', 'nodeViewService', 'fxAppTreeService', 'fxAppModalService', 'guardianService',
	function($scope, $rootScope, $http, fxAppService, nodeViewService, fxAppTreeService, fxAppModalService, guardianService) {

	$scope.fxAppService = fxAppService;
	$scope.fxAppTreeService = fxAppTreeService;
	$scope.nodeViewService = nodeViewService;

    $scope.tpsBoxHeight = 370;

    $scope.localProductName = guardianService.localProductName();

	$scope.forms = {
		nodesStats:   1,
		nodesForm:     2
	};

	$.AdminLTE.layout.fix();
}]);
