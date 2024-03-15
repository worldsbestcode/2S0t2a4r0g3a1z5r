/**
 * Component for displaying stats about the balancer such as connections opened or closed over time
 */
fxApp.component('nodeBalancerStats', {
    templateUrl: 'components/sections/nodeView/nodeBalancerStats.html',
    controller: ['$scope', '$uibModal', 'socketio', 'chartFactory', 'nodeViewService', function($scope, $uibModal, socketio, chartFactory, nodeViewService) {

        $scope.nodeViewService = nodeViewService;

        // Initialize the charts
        $scope.chartLastChecked = new Date(0).toISOString();
        $scope.chartLastUpdated = new Date(0).toISOString();
        $scope.statCharts = createInitialChartData();
        $scope.statMap = {
            'Balancer Connection Sum': {},
            'Balancer Open Connection Count': {}
        };

        // List of charts to make requests for when an update event occurs
        var statChartKeys = ['currConnChart'];

        // Pagination data for charts
        $scope.pagination = {
            'connChart': { currentPage: 1, totalPages: 3 },
            'currConnChart': { currentPage: 1, totalPages: 3 }
        };

        // Currently selected date range in stat charts
        // Last week would be 6 days ago at start of day
        $scope.statSelectedDate = {
            'connChart': { 'begin': nodeViewService.diffDays(nodeViewService.startOfDay(), -6), 'end': nodeViewService.endOfDay() },
            'currConnChart': { 'begin': nodeViewService.diffDays(nodeViewService.startOfDay(), -6), 'end': nodeViewService.endOfDay() }
        };
        $scope.isLiveMap = nodeViewService.checkIsLive($scope.statSelectedDate);

        // Currently selected series in stat charts
        $scope.statGroupOptions = nodeViewService.getGroupTypes();

        // Called when changing the data in the chart
        $scope.changeSeriesOrDate = function(chartName, index) {
            // Selection changed, so update which charts are live
            $scope.isLiveMap = nodeViewService.checkIsLive($scope.statSelectedDate);

            // Determine what is selected for the chart
            var period = $scope.statSelectedDate[chartName];
            var groupName = nodeViewService.getCurrentSelectedNodeDeviceGroupName();

            var isLive = $scope.isLiveMap[chartName];

            // Reset the current page if none selected
            if (!index) {
                $scope.pagination[chartName].currentPage = 1;
            }

            nodeViewService.retrieveStats(
                period.begin,
                period.end,
                nodeViewService.managerTypeFromChartName(chartName),
                nodeViewService.statNameFromChartName(chartName),
                groupName,
                index
            ).then(function(result) {
                // Clear the selected group name data before continuing
                nodeViewService.clearStatMapByTypeAndGroup(
                    nodeViewService.statNameFromChartName(chartName),
                    groupName,
                    $scope.statMap
                );

                // Push the retrieved data points into the map of stats data
                result.data.map(function(item) {
                    nodeViewService.updateStatMap(
                        item,
                        $scope.statMap,
                        nodeViewService.statNameFromChartName(chartName),
                        nodeViewService.managerTypeFromChartName(chartName)
                    );
                });

                // Update page count
                $scope.pagination[chartName].totalPages = result.numChunks;
            }).finally(function() {
                // Update the timestamp displayed to the user
                $scope.chartLastUpdated = new Date().toISOString();

                // Update the stat chart
                var chartSeriesParams = nodeViewService.chartSeriesParamsFromChartName(chartName);
                nodeViewService.updateStatChart(
                    chartSeriesParams.seriesName,
                    $scope.statMap[nodeViewService.statNameFromChartName(chartName)][groupName],
                    $scope.statCharts[nodeViewService.nvd3DataNameFromChartName(chartName)],
                    chartSeriesParams.keyNameX,
                    chartSeriesParams.keyNameY,
                    chartSeriesParams.transformationFunc,
                    $scope.pagination[chartName],
                    $scope.statSelectedDate[chartName]
                );
            });
        };

        $scope.nextPage = function(chartName) {
            if (nodeViewService.nextPage($scope.pagination, chartName)) {
                $scope.changeSeriesOrDate(chartName, $scope.pagination[chartName].currentPage - 1);
            }
        };
        $scope.prevPage = function(chartName) {
            if (nodeViewService.prevPage($scope.pagination, chartName)) {
                $scope.changeSeriesOrDate(chartName, $scope.pagination[chartName].currentPage - 1);
            }
        };

        // Initialize the charts
        nodeViewService.iterStatChartNames(statChartKeys, $scope.changeSeriesOrDate);

        // When the type changes update the graphs
        $scope.$watch('nodeViewService.getCurrentSelectedNodeDeviceGroupName()', function (groupName) {
            // Update the time last checked to prevent excessive requests
            $scope.chartLastChecked = new Date().toISOString();

            if (groupName) {
                nodeViewService.iterStatChartNames(statChartKeys, $scope.changeSeriesOrDate);
            }
        });

        // Socket.io listener
        $scope.$on('socket:notify_external_change', function(event, data) {
            // Only update the chart if the update is for a balancer stat and a minimum time has elapsed
            if (nodeViewService.checkStat(data.objectData) &&
                nodeViewService.checkTimeSinceChartLastChecked($scope.chartLastChecked)) {

                // Update the time last checked to prevent excessive requests
                $scope.chartLastChecked = new Date().toISOString();

                // Only update if the chart is live and the user is actually
                // looking at the most recent data points
                nodeViewService.iterStatChartNames(statChartKeys, function(chartName) {
                    var paginationData = $scope.pagination[chartName];
                    if ($scope.isLiveMap[chartName] && paginationData.currentPage === 1) {
                        $scope.changeSeriesOrDate(chartName, $scope.pagination[chartName].currentPage - 1);
                    }
                });
            }
        });

        // Initial chart data
        function createInitialChartData() {
            return {
                connTitle: 'Cumulative Connections',
                connIcon: 'bar-chart',
                connData: [{
                    'key': 'Connection Count',
                    'values': []
                }],
                connOptions: chartFactory.multiBarChart({
                    height: 250,
                    chartTitle: '',
                    colors: ['#0084A3', '#005164', '#06CCFB', '#006982'],
                    xGetter: function(d) {
                        return d.x;
                    },
                    yGetter: function(d) {
                        return d.y;
                    },
                    xAxisLabel: 'Time',
                    xAxisTickFormat: function(d) {
                        return d;
                    },
                    yAxisLabel: 'Connection Count',
                    yAxisTickFormat: function(d) {
                        return d.toLocaleString();
                    }
                }),
                currConnTitle: 'Currently Open Connections',
                currConnIcon: 'bar-chart',
                currConnData: [{
                    'key': 'Connection Count',
                    'values': []
                }],
                currConnOptions: chartFactory.lineChart({
                    height: 250,
                    chartTitle: '',
                    colors: ['#0084A3', '#005164', '#06CCFB', '#006982'],
                    xGetter: function(d) {
                        return d.x;
                    },
                    yGetter: function(d) {
                        return d.y;
                    },
                    xAxisLabel: 'Time',
                    xAxisTickFormat: function(d) {
                        return d3.time.format('%Y-%m-%d %H:%M:%S')(new Date(d));
                    },
                    xAxisStaggerLabels: true,
                    xAxisLabelDistance: 10,
                    yAxisLabel: 'Connection Count',
                    yAxisTickFormat: function(d) {
                        return d3.format('d')(d);
                    },
                    interpolate: 'step-after',
                    margin: {
                        right: 60,
                    },
                })
            };
        }

        // Called when user clicks the expand button for a chart
        $scope.openModal = function(statSelected) {
            $uibModal.open({
                templateUrl: 'components/sections/nodeView/nodeStatsModal.html',
                windowTemplateUrl: 'directives/fxWideModal.html',
                resolve: {
                    statSelected: function() {
                        return statSelected;
                    },
                    statOptions: function() {
                        switch (statSelected) {
                            case 'connChart':
                                return $scope.statCharts.connOptions;
                            case 'currConnChart':
                                return $scope.statCharts.currConnOptions;
                        }
                    },
                    statIcon: function() {
                        switch (statSelected) {
                            case 'connChart':
                                return $scope.statCharts.connIcon;
                            case 'currConnChart':
                                return $scope.statCharts.currConnIcon;
                        }
                    },
                    statTitle: function() {
                        switch (statSelected) {
                            case 'connChart':
                                return $scope.statCharts.connTitle;
                            case 'currConnChart':
                                return $scope.statCharts.currConnTitle;
                        }
                    },
                    statData: function() {
                        switch (statSelected) {
                            case 'connChart':
                                return $scope.statCharts.connData;
                            case 'currConnChart':
                                return $scope.statCharts.currConnData;
                        }
                    }
                },
                controller: 'nodeStatModalCtrl'
            })
        };

    }]
});
