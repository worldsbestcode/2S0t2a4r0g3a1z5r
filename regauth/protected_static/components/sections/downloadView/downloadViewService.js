/**
 * Provides commonly used functions for the download view
 *
 * @returns {object}    helper functions injected into the download view controller
 */

var downloadViewService = fxApp.factory('downloadViewService',
    ['$http', '$q', 'fxAppService', 'fxAppViewService',
    function($http, $q, fxAppService, fxAppViewService) {

        /**
         * Makes a request for PKCS#12 file
         *
         * @param   {string}     uniqueID - Unique ID of CSR to download PKCS#12 file from
         * @param   {string}     password - Password for pkcs#12 file
         * @param   {string}     clear_pki - Option on whether to clear the pkcs#12 file or not
         * @returns {promise}    resolved upon receiving the response
         */
        function getDownload(uniqueID, password, clear_pki) {
            var deferred = $q.defer();

            var downloadQuery = {
                "uniqueID" :  uniqueID,
                "password":   fxAppViewService.hexEncode(password),
                "clear_pki" : clear_pki
            };

            $http.post(window.apipath('/download'), downloadQuery).success(function(data) {
                deferred.resolve(data);
            });

            return deferred.promise;
        }

        return {
            getDownload: getDownload,
            downloadString: fxAppViewService.downloadString,
            spacesToUnderscores: fxAppViewService.spacesToUnderscores,
            hexToArrayBuffer: fxAppViewService.hexToArrayBuffer
        };
    }]
);
