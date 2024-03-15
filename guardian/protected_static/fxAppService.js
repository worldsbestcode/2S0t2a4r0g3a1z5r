/**
 * Provides functions accessible to the entire web app
 *
 * @returns {object}    helper functions injected anywhere
 */

var fxAppService = fxApp.factory('fxAppService',
	['$rootScope', '$http',
	function($rootScope, $http) {

    var views = [
        'nodesView',
        'configView',
        'peerView',
    ];

    var viewToDisplay = views[0];
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
    try {
        loginData.id = login_info.id;
        loginData.users = login_info.users;
        loginData.name = login_info.name;
        loginData.primaryIdentity.id = login_info.primaryIdentity.id;
        loginData.primaryIdentity.name = login_info.primaryIdentity.name;
    }
    catch (e) {
    }
	}

	/**
	 * Singleton accessor for the FxCNG plugin.
	 * 
	 * @returns The FxCNG plugin.
	 */
	function getFXCNGPlugin() {
		
		if (!isInternetExplorer()) {
			return null;
		}

		else if (!fxcng) {
			fxcng = new FxCNGPlugin();
		}

		return fxcng;
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

    /**
     * Check if the sidebar is currently displayed
     * @return {boolean}  True if displayed false otherwise
     */
    function isRightSidebarShown() {
        return $('body').hasClass('control-sidebar-open');
    }

    /**
     * Set the right sidebar shown status
     * @param {boolean}  shown  If true show the right sidebar if false hide it
     */
    function setRightSidebarShown(shown) {
        var currentShown = isRightSidebarShown();
        if (currentShown !== shown) {
            $('a.control-sidebar-btn').click();
        }
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
		getLoginData: function() {
			return loginData;
		},
		getFXCNGPlugin: getFXCNGPlugin,
        setRightSidebarShown: setRightSidebarShown,
        isRightSidebarShown: isRightSidebarShown,
        isAnonymous: isAnonymous,
		isInternetExplorer: isInternetExplorer,
		isSafari: isSafari
	};
}]);
