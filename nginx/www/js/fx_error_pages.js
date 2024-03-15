var fxErrorPage = angular.module('fxErrorPage', []);

var errorPageCtrl = fxErrorPage.controller('errorPageCtrl',
	['$scope', '$http', '$location', function($scope, $http, $location) {

	function setErrorCode(errorCode) {
		$scope.errorCode = "ERR: " + errorCode;
	}

	// Success or failure doesn't matter, just grab the status code.
	$http.get(document.location.href)
		.error(function(response, status) {
			setErrorCode(status);
		}
	);
}]);

