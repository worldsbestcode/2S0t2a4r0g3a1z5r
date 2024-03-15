// App prefix
window.api_prefix = "/regauth/v1";
window.apipath = function(path) {
  return window.api_prefix + path;
}

/**
 * Instantiate the app
 */
var fxApp = angular.module('fxApp',
	['ngAnimate', 'angularBootstrapNavTree', 'ui.bootstrap']
);

/**
 * Controller for the header in header.html
 */
var headerCtrl = fxApp.controller('headerCtrl',
	['$scope', 'fxAppService',
	function($scope, fxAppService) {

	$scope.fxAppService = fxAppService;

	// Show/hide the right sidebar when in csr view
	$scope.$watch('fxAppService.getView()', function() {

		var view = fxAppService.getView();
		var views = fxAppService.getViews();
		var inCsrView = view >= views['csrViewPending'] && view <= views['csrViewFilter'];

		if ($scope.rightSidebarShown && !inCsrView) {
			$('a.control-sidebar-btn').click();
		}
		else {
			if (!$scope.rightSidebarShown && inCsrView) {
				$('a.control-sidebar-btn').click();
			}
		}
	});

	// Update $scope.rightSidebarShown when sidebar is opened/closed
	$('body').on('addClass toggleClass removeClass', function(){
		setTimeout(function() {
			$scope.rightSidebarShown = $('body').hasClass('control-sidebar-open');
			$scope.$apply();
		}, 0);
	});
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
 * Controller for the right sidebar in landing.html
 */
var rightSidebarCtrl = fxApp.controller('rightSidebarCtrl',
	['$rootScope', '$scope', 'fxAppService', 'fxAppTreeService', 'fxAppFilterService',
	function($rootScope, $scope, fxAppService, fxAppTreeService, fxAppFilterService) {

	$scope.fxAppService = fxAppService;
	$scope.fxAppTreeService = fxAppTreeService;
	$scope.fxAppFilterService = fxAppFilterService;
}]);

/**
 * Controller for the content wrapper in landing.html
 */
var contentCtrl = fxApp.controller('contentCtrl',
	['$scope', '$rootScope', 'fxAppService', 'fxAppModalService', 'fxAppFilterService',
	function($scope, $rootScope, fxAppService, fxAppModalService, fxAppFilterService) {

	$scope.fxAppService = fxAppService;
	$scope.fxAppModalService = fxAppModalService;
	$scope.fxAppFilterService = fxAppFilterService;

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
