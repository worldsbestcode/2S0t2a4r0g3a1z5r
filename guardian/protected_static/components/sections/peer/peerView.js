peerViewController.$inject = ['$scope', '$uibModal', 'peerService', 'fxAppStringService', 'guardianService', 'socketio'];
function peerViewController($scope, $uibModal, peerService, fxAppStringService, guardianService, socketio) {
    function processPeer(peer) {
        try {
            // Put peer content into rows
            peer.contentRows = {
                'IP Address': peer.ip + ':' + peer.port,
                'Version': peer.version,
                'Serial': peer.serial,
                'State': fxAppStringService.capitalizeFirstLetter(peer.state),
                'Last Connected': peer.lastConnect,
                'Last Sent': peer.lastSend,
                'FIPS Mode': fxAppStringService.capitalizeFirstLetter(peer.secureMode.fips),
                'PCI-HSM Mode': fxAppStringService.capitalizeFirstLetter(peer.secureMode.pciHSM),
            };
        }
        catch (e) {
            console.error('Failed to map peer attributes to content rows: %s.', e.message);
        }
    }

    $scope.$on('socket:update_object', function(ev, data) {
        // The object is in a string form. Parse it out into a map
        var objectData = data.objectData;

        // We're getting update notifications for all objects. Filter only for peer MOs
        if (objectData.objectType === 'PEER') {
            processPeer(objectData)
            guardianService.updateObjectInArray($scope.peerModel.peers, objectData);
        }
    });

    $scope.$on('socket:delete_object', function(ev, data) {
        var objectData = data.objectData;
        if (objectData.objectType === 'PEER') {
            guardianService.removeObjectFromArray($scope.peerModel.peers, objectData.objectID);
        }
    });

    $scope.localProductName = guardianService.localProductName();

    $scope.mappings = {
        peerHeaderMapping: {
            name : 'Name',
            peerTypeString: 'Type',
            stateString: 'State'
        },
    }

    $scope.peerModel = {
        currentSelection: {},
        peers: [],
    };

    peerService.getPeers().then(function (peers) {
        peers.forEach(function (peer) {
            processPeer(peer);
        });

        $scope.peerModel.peers = peers;
    }, function (error) {
        console.error('Failed to query for peers: %s', error.message);
    });

    $scope.openModal = function(peer) {
        $scope.peer = peer;
        $uibModal.open({
            templateUrl: 'components/sections/peer/peerEventModal.html',
            windowTemplateUrl: 'directives/fxWideModal.html',
            controller:'peerEventModalCtrl',
            resolve: {
                peer: function() {
                    return $scope.peer;
                },
            },
        });
    };
};

fxApp.controller('peerViewController', peerViewController);

fxApp.controller('peerEventModalCtrl', ['$scope', function($scope) {
    $scope.cancel = function () {
        $scope.$dismiss('cancel');
    };
}]);

fxApp.component('peerView', {
    templateUrl: 'components/sections/peer/content.html',
    controller: 'peerViewController',

});

