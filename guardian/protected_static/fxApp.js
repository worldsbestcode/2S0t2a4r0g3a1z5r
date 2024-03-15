// App prefix
window.api_prefix = "/guardian/v1";
window.apipath = function(path) {
  return window.api_prefix + path;
}

/**
 * Instantiate the app
 */
var fxApp = angular.module('fxApp',
	['ngAnimate', 'angularBootstrapNavTree', 'btford.socket-io', 'nvd3', 'ui.bootstrap', 'fxLogin']
);

/**
 * Controller for the header in header.html
 */
var headerCtrl = fxApp.controller('headerCtrl',
	['$scope', 'fxAppService', 'guardianService',
	function($scope, fxAppService, guardianService) {

	$scope.fxAppService = fxAppService;
	$scope.guardianService = guardianService;
	$scope.rightSidebarEnabled = false;

	// Show/hide the right sidebar when in the config view
	$scope.$watch('fxAppService.getView()', function(view) {
        // Disable the sidebar for any view that isn't "configView"
        $scope.rightSidebarEnabled = view === 'configView';
        // Hide the sidebar if it's being shown
        fxAppService.setRightSidebarShown(false);
	});

	// Enable the toggle for the right sidebar when needed
	function enableRightSidebar(oldVal, newVal) {
		// Right sidebar is only used in "configView" for now
		if (fxAppService.getView() !== 'configView') {
			$scope.rightSidebarEnabled = false;
		}
		// Otherwise, enable the sidebar because a group or device was just selected
		else {
			$scope.rightSidebarEnabled = true;
		}
	}
	$scope.$watch('guardianService.selectedObjectID', enableRightSidebar);
	$scope.$watch('guardianService.selectedObjectParentID', enableRightSidebar);
}]);

/**
 * Controller for the sidebar in header.html
 */
var sidebarCtrl = fxApp.controller('sidebarCtrl',
	['$scope', 'fxAppService',
	function($scope, fxAppService) {

	$scope.fxAppService = fxAppService;
}]);

/**
 * Controller for the body in landing.html
 */
var rightSidebarCtrl = fxApp.controller('rightSidebarCtrl',
	['$rootScope', '$window', '$scope', 'fxAppService',
	function($rootScope, $window, $scope, fxAppService) {

	$scope.fxAppService = fxAppService;

    // Update $scope.rightSidebarShown when sidebar is opened/closed
	$('body').on('addClass toggleClass removeClass', function(){
		setTimeout(function() {
            // required to update the view
			$scope.$apply();
		}, 0);
	});

    $scope.$on('$includeContentLoaded', function(event) {
        // Grab DOM from warning.html's document.
        $(".titleBar").remove();
        $(".copyright").remove();
        $(".container").css("min-width", "300px");
        $.AdminLTE.layout.fix();
    });
}]);

/**
 * Controller for the content wrapper in landing.html
 */
var contentCtrl = fxApp.controller('contentCtrl',
	['$scope', '$rootScope', 'fxAppService', 'fxAppModalService',
	function($scope, $rootScope, fxAppService, fxAppModalService) {

	$scope.fxAppService = fxAppService;
	$scope.fxAppModalService = fxAppModalService;

	// Notifies user that the session has expired, or the backend was disconnected
	$rootScope.$on('sessionExpire', function(e) {
		fxAppModalService.showModal(
			'Session Expired!',
			'Your session has expired due to inactivity. Please click OK to log back in.',
			function(event){
				location = '/';
			}
		);
	});
}]);

/**
 * Factory to generate http interceptor that warns user of session expiration
 */
fxApp.factory('expiredInterceptor', ['$q', '$rootScope', function($q, $rootScope) {
	var responseInterceptor = {
		response: function(response) {
			return response;
		}, 
		responseError: function(response) {
			if (response.status === 401) {
				$rootScope.$broadcast('sessionExpire');
			} else {
				return $q.reject(response);
			}
		}
	}
	return responseInterceptor;
}]);

/** 
 * Factory for socket io connections
 */
fxApp.factory('socketio', ['$rootScope', 'socketFactory', function($rootScope, socketFactory) {
    var appSocket = socketFactory({
        ioSocket: io.connect('/object', {path: '/guardian/socket.io'})
    });

    appSocket.forward('update_object');
    appSocket.forward('delete_object');
    appSocket.forward('notify_external_change');

    $rootScope.$on('sessionExpire', function () {
        appSocket.disconnect();
    });

    return appSocket;
}]);

/**
 * Adds interceptor to httpProvider
 */
fxApp.config(['$httpProvider', '$locationProvider', function($httpProvider, $locationProvider) {
	$httpProvider.interceptors.push('expiredInterceptor');
  $httpProvider.defaults.xsrfCookieName = "FXSRF-TOKEN";
  $httpProvider.defaults.xsrfHeaderName = "X-FXSRF-TOKEN";
    $locationProvider.html5Mode({ 
        enabled: true, 
        requireBase: false,
        rewriteLinks: false
    });
}]);

/**
 * Allows us to register callbacks on CSS class changes
 */
(function ($) {
	var methods = ['addClass', 'toggleClass', 'removeClass'];

	$.each(methods, function (index, method) {
		var originalMethod = $.fn[method];

		$.fn[method] = function () {
			var result = originalMethod.apply(this, arguments);
			var oldClass = '';
			var newClass = '';

			// might have just added a class to a node without classes
			if (oldClass) {
				oldClass = this[0].className;
			}

			// might have just removed the last class from the node
			if (newClass) {
				newClass = this[0].className;
			}

			this.trigger(method, [oldClass, newClass]);

			return result;
		};
	});
}(window.jQuery));
