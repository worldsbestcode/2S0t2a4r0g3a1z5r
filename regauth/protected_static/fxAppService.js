/**
 * Provides functions accessible to the entire web app
 *
 * @returns {object}    helper functions injected anywhere
 */

var fxAppService = fxApp.factory('fxAppService',
	['$rootScope', '$http',
	function($rootScope, $http) {

	var views = {
		placeholder:      0,
		csrViewPending:   1,
		csrViewSigned:    2,
		csrViewDenied:    3,
		csrViewAll:       4,
		csrViewFilter:    5,
		submitView:       6
	};

	var viewToDisplay = views['csrViewAll'];
	var isLoading = false;

	var loginData = {};

	var fxcng = null;

	/**
	 * Tests LocalStorage support
	 *
	 * @returns {boolean}    whether the browser supports LocalStorage
	 */
	function hasLocalStorage() {
		try {
			var test = 'test';
			localStorage.setItem(test, test);
			localStorage.removeItem(test);
			return true;
		}
		catch (event) {
			return false;
		}
	}

	/**
	 * Gets the login information
	 *
	 * @returns {object}    the login information
	 */
	function setLoginData() {
    try {
      $http.get(window.apipath('/logininfo'), {responseType: 'text'}).then(function(response) {
        parseLoginInfo(JSON.parse(JSON.stringify(response.data.response)));
      });
    }
    catch (e) {
    }
	}

	/**
	 * Determines the view permissions from the string "login_info.permissions"
	 */
	function parseLoginInfo(login_info) {
		function hasUpload(permissions) {
            return permissions.filter(function(permissionName) {
				return permissionName === "Upload";
			}).length > 0;
		}

		function hasApprove(permissions) {
            return permissions.filter(function(permissionName) {
				return permissionName === "Approve";
			}).length > 0;
		}

    // These are all the fields checked
    loginData = {
      id: -1,
      users: [],
      name: '',
      primaryIdentity: {
        id: -1,
        name: '',
      },
    }
    var uploadPerm = false;
    var approvePerm = false;
    try {
        var certManage = login_info.permissions['CertManage'] || [];
        var requestApproval = login_info.permissions['RequestApproval'] || [];
        var uploadPerm = hasUpload(certManage);
        var approvePerm = hasApprove(requestApproval);
        loginData.id = login_info.id;
        loginData.users = login_info.users;
        loginData.name = login_info.name;
        loginData.primaryIdentity.id = login_info.primaryIdentity.id;
        loginData.primaryIdentity.name = login_info.primaryIdentity.name;
    }
    catch (e) {
    }

		loginData.permissions = {
			uploadPerm: uploadPerm,
			approvePerm: approvePerm,
			submitter: uploadPerm,
			vetter: approvePerm
		};

		// set submitter view as default if submitter
		if (loginData.permissions.submitter) {
			viewToDisplay = views['submitView'];
        } else if (loginData.permissions.vetter) {
            viewToDisplay = views['csrViewPending']
        }
	}

	/**
	 * Singleton accessor for the FxCNG plugin.
	 *
	 * @returns The FxCNG plugin.
	 */
	function getFXCNGPlugin() {
    // Deprecated
    return null;
	}

	/**
	 * Lets us know if we're running Internet Explorer.
	 *
	 * @returns True if we are, false if we're not.
	 */
	function isInternetExplorer() {
		var sUserAgent = window.navigator.userAgent;

		var iMSIE = sUserAgent.indexOf('MSIE ');
		var iTrident = sUserAgent.indexOf('Trident/');
		var iEdge = sUserAgent.indexOf('Edge/');

		if (iMSIE > 0 || iTrident > 0 || iEdge > 0) {
			return true;
		}

		return false;
	}

	/**
	 * Lets us know if we're running Safari.
	 *
	 * @returns True if we are, false if we're not.
	 */
	function isSafari() {
		// Check the user agent string
		var hasSafariUA = window.navigator.userAgent.toLowerCase().indexOf('safari') > -1;

		// Check if the Safari browser API is present
		var hasSafariAPI = window.safari !== undefined;

		if (hasSafariUA && hasSafariAPI) {
			return true;
		}

		return false;
	}

	setLoginData();

    /**
     * Check if the user is anonymous
     * @returns {boolean}  true if the user is anonymous false otherwise
     */
    function isAnonymous() {
        return loginData.id === '1000';
    }

	return {
		setView: function(view) {
			viewToDisplay = view;
			$rootScope.$emit('viewChange');
		},
		getView: function() {
			return viewToDisplay;
		},
		getViews: function() {
			return views;
		},
		setLoading: function() {
			isLoading = true;
		},
		resetLoading: function() {
			isLoading = false;
		},
		getLoading: function() {
			return isLoading;
		},
        setLoginData: setLoginData,
		getLoginData: function() {
			return loginData;
		},
		getFXCNGPlugin: getFXCNGPlugin,
        isAnonymous: isAnonymous,
		isInternetExplorer: isInternetExplorer,
		isSafari: isSafari
	};
}]);
