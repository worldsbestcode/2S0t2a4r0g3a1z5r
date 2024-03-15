/**
 * The base HTML of the download view
 */
fxApp.component('downloadView', {
    templateUrl: 'components/sections/downloadView/content.html'
});

/**
 * The download form
 */
fxApp.component('downloadForm', {
    templateUrl: 'components/sections/downloadView/downloadForm.html',
    bindings: {
        downloadcert: '=',
        formdata:     '='
    }
});

/**
 * The download view controller
 */
var downloadViewCtrl = fxApp.controller('downloadViewCtrl',
    ['$scope', '$rootScope', '$location', '$http', 'fxAppService', 'fxAppModalService', 'downloadViewService',
    function($scope, $rootScope, $location, $http, fxAppService, fxAppModalService, downloadViewService) {

    $scope.uniqueID = $location.search().uniqueID;

    // User is redirected if "uniqueID" query string parameter is missing
    if (!$scope.uniqueID) {
        window.location = '/regauth';
    }

    // Set the form data
    $scope.fxForms = this;
    $scope.fxForms.downloadForm = {
        data: {
            password : "",
            clear_pki : false
        },
        downloadCertCallback: function() {
            downloadViewService.getDownload(
                $scope.uniqueID,
                $scope.fxForms.downloadForm.data.password,
                $scope.fxForms.downloadForm.data.clear_pki
            ).then(function(data) {
                if (data.result === "Failure") {
                    fxAppModalService.showModal('Error', data.message);
                }
                else {
                    // Download the file
                    downloadViewService.downloadString(
                        downloadViewService.hexToArrayBuffer(data.pki),
                        downloadViewService.spacesToUnderscores(data.name) + '_pkcs12.der');

                    // User is redirected after download
                    window.location = '/regauth';
                }
            });
        }
    };

    $.AdminLTE.layout.fix();
}]);
