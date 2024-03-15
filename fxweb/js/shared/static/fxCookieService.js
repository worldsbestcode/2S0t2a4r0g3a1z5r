/**
 * The cookie module.
 */
var fxCookieUtil = angular.module('fxCookieUtil', []);

/**
 * Provides common functions for dealing with cookies.
 *
 * @returns {object}    Helper functions for cookies.
 */
var fxAppCookieService = fxCookieUtil.factory('fxCookieService',
    ['$q', '$timeout',
    function($q, $timeout) {

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
     * Tests cookie support
     *
     * @returns {boolean}    whether the browser has cookies enabled
     */
    function hasCookiesEnabled() {
        return window.navigator.cookieEnabled;
    }

    /**
     * Attempts to store the login info in LocalStorage or a cookie
     *
     * @param   {string}     storage_key - The key to store the value under.
     * @param   {string}     storage_val - The value to store.
     * 
     * @returns {boolean}    Whether the information was successfully stored.
     */
    function tryToStore(storage_key, storage_val) {
        var testResults = {
            cookie: hasCookiesEnabled()
        };

        if (testResults.cookie) {
            document.cookie = storage_key + '=' + encodeURIComponent(storage_val);
            return true;
        }
        else {
            return false;
        }
    }

    /**
     * Attempts to retrieve data from a cookie
     *
     * @param   {string}     key_name - The key the data is stored under
     *
     * @returns {string}     result - The retrieved value or an empty string
     */
    function cookieRetrieve(keyName) {
        var result = '';
        document.cookie.split(";").map(function (kvPair) {
            var kvPairArr = kvPair.split('=');
            if (kvPairArr[0].trim() === keyName.trim()) {
                result = JSON.parse(decodeURIComponent(kvPairArr[1]));
            }
        });

        return result;
    }

    /**
     * Grabs the previous server response to whatever we sent.
     *
     * @param {int} object_id - The ID of the remote device we're getting login info for.
     *                          Can be left out, will query the main login cookie instead.
     * @returns {string}    The last server response. Blank string if nothing.
     */
    function getPreviousLoginInfo(object_id) {

        var previous_login_data = null;
        var previous_login_message = "";
        var cookie_name = 'login_info';

        if (object_id) {
            cookie_name += "_" + object_id;
        }

        var testResults = {
            cookie: hasCookiesEnabled()
        };

        if (testResults.cookie) {
            previous_login_data = cookieRetrieve(cookie_name);
        }

        if (previous_login_data) {
            previous_login_message =
                'message' in previous_login_data ? previous_login_data.message : "";
        }

        return previous_login_message;
    }

    /**
     * Clears the previous login message
     * 
     * @param {string} cookie_name - The name of the cookie that holds the login message.
     * @returns {boolean} Whether the login message was cleared.
     */
    function clearPreviousLoginMessage(cookie_name) {
        var testResults = {
            cookie: hasCookiesEnabled()
        };

        if (!cookie_name) {
            cookie_name = "login_info";
        }

        // Copy the login_info
        var previous_login_data = "";
        if (testResults.cookie) {
            previous_login_data = cookieRetrieve(cookie_name);
        }

        // Clear the login message
        previous_login_data.message = "";

        // Set the login_info
        return tryToStore(cookie_name, JSON.stringify(previous_login_data));
    }

    /**
     * Slices up the cookie that contains our authorized remote device/group IDs
     * and returns it to the caller.
     * 
     * @returns {list} All the authorized remote device/group IDs.
     */
    function getAuthorizedRemoteObjectIDs() {

        var authorized_ids = [];

        var testResults = {
            cookie: hasCookiesEnabled()
        };

        if (testResults.cookie) {
            authorized_ids = cookieRetrieve("authed_ids");
        }

        return authorized_ids;
    }

    return {
        hasLocalStorage: hasLocalStorage,
        hasCookiesEnabled: hasCookiesEnabled,
        tryToStore: tryToStore,
        cookieRetrieve: cookieRetrieve,
        getPreviousLoginInfo: getPreviousLoginInfo,
        clearPreviousLoginMessage: clearPreviousLoginMessage,
        getAuthorizedRemoteObjectIDs: getAuthorizedRemoteObjectIDs
    };

}]);
