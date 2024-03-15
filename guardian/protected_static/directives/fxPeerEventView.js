fxApp.directive('fxPeerEventView', function fxPeerEventView() {
    return {
        templateUrl: 'directives/fxPeerEventView.html',
        scope: {
            peer: '=',
            maxRowCount: '=maxrowcount',
            events: '@events',
            activeIndex: '@active',
        },
        controller: [
            '$scope',
            '$interval',
            'peerService',
            'guardianService',
            'socketio',
            'fxAppStringService',
            function fxPeerEventView($scope, $interval, peerService, guardianService, socketio, fxAppStringService) {

                var maxEventLogCount = 1000;

                $scope.$on('socket:update_object', function(ev, data) {
                    // The object is in a string form. Parse it out into a map
                    var objectData = data.objectData;

                    // We're getting update notifications for all objects. Filter only for EVENT MOs
                    if (objectData.objectType === 'EVENT') {

                        // Only pay attention if it's for our item's peer object
                        if (objectData.peerID === $scope.peer.objectID) {
                            postPeerEvent(objectData, 'update');
                        }
                    }
                });

                $scope.$on('socket:delete_object', function(ev, data) {
                    var objectData = data.objectData;
                    if (objectData.objectType === 'EVENT') {
                        postPeerEvent(objectData, 'delete');
                    }
                });

                $scope.pendingEvents = []
                function postPeerEvent(event, action) {
                    $scope.pendingEvents.push({
                        event: event,
                        action: action,
                    })
                }

                function deleteEvent(event) {
                    guardianService.removeObjectFromArray($scope.events, event.objectID);
                }

                function updateEvent(event) {
                    guardianService.updateObjectInArray($scope.events, event);
                    if ($scope.events.length > maxEventLogCount) {
                        $scope.events.length = maxEventLogCount;
                    }
                }

                function updateEvents() {
                    if (!$scope.pendingEvents.length) {
                        return;
                    }

                    $scope.pendingEvents.forEach(function(eventInfo) {
                        if (eventInfo.action === 'update') {
                            updateEvent(eventInfo.event);
                        }
                        else if (eventInfo.action === 'delete') {
                            deleteEvent(eventInfo.event);
                        }
                    })

                    $scope.pendingEvents = []

                    reformSlides();

                    $scope.busy = false;
                }
                $interval(updateEvents, 500);

                // Indicate that we're busy until we retrieve the first batch of events
                $scope.busy = true;

                // Grab all the events for our peer
                $scope.events = [];
                $scope.slides = [];
                peerService.getEventsForPeers([$scope.peer.objectID]).then(function (events) {
                    events.forEach(function(event) {
                        postPeerEvent(event, 'update');
                    });
                }, function (error) {
                    console.error('Failed to retrieve events for peer "%s: %s', $scope.peer.name, error);
                    $scope.busy = false;
                });

                $scope.tableOptions = {
                    headers: [
                        {
                            name: 'Time Start',
                            attr: 'timeStart',
                            colSize: '1',
                        },
                        {
                            name: 'Time End',
                            attr: 'timeEnd',
                            colSize: '1',
                        },
                        {
                            name: 'Duration',
                            attr: 'duration',
                            colSize: '1',
                        },
                        {
                            name: 'Description',
                            attr: 'description',
                            colSize: '2',
                        },
                    ],
                };

                /**
                 * Builds a comma seperated string holding the last 1000
                 * the peering events.
                 */
                function makeEventsString() {
                  var str = '';
                  $scope.events.forEach(function(event) {
                    $scope.tableOptions.headers.forEach(function (header) {
                      str += event[header.attr] + ',';
                    });
                    str += '\n';
                  });
                  return str;
                };

                $scope.downloadPeerLogs = function () {
                  fxAppStringService.downloadPlainTextString(makeEventsString(), 'PeeringEvents')
                };

                function reformSlides() {
                    var chunkSize = 15;
                    for (var i = 0; i < $scope.events.length && i < $scope.maxRowCount; i += chunkSize) {
                        var slideIndex = Math.floor(i / chunkSize);
                        if ($scope.slides.length <= slideIndex) {
                            $scope.slides.push({
                                index: slideIndex,
                                events: [],
                            });
                        }

                        var slide = $scope.slides[slideIndex];
                        var endOfChunk = i + chunkSize  > $scope.maxRowCount ? $scope.maxRowCount : i + chunkSize;
                        slide.events = $scope.events.slice(i, endOfChunk);
                    }
                }
            },
        ],
    };
});
