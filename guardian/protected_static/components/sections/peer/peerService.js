fxApp.factory('peerService',
    ['fxAppViewService',
    function (fxAppViewService) {
        function getPeers() {
            var peers = [];
            try {
                peers = fxAppViewService.getAllObjectsForTypes(['PEER']);
            }
            catch (e) {
                console.error('Failed to retrieve all peers: %s.', e.message);
            }

            return peers;
        }

        function getEvents() {
            var events = [];
            try {
                events = fxAppViewService.getAllObjectsForTypes(['EVENT']);
            }
            catch (e) {
                console.error('Failed to retrieve all events: %s.', e.message);
            }

            return events;
        }

        function getEventsForPeers(peerIDs) {
            // Grab all the events for peers matching the peerIDs
            return getEvents().then(function (events) {
                return events.filter(function(event) {
                    return peerIDs.includes(event.peerID);
                }, function (error) {
                    console.error('Failed to query all events for peer: %s', error.message);
                });
            });
        }

        return {
            getPeers: getPeers,
            getEvents: getEvents,
            getEventsForPeers: getEventsForPeers,
        };
    }]
);

