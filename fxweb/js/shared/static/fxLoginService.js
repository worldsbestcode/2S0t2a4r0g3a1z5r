/**
 * The cookie module.
 */
var fxLoginUtil = angular.module('fxLoginUtil', ['fxCookieUtil']);

/**
 * Provides common functions for logging into the remote server.
 *
 * @returns {object}    Helper functions for logging in.
 */
var fxLoginService = fxLoginUtil.factory('fxLoginService',
	['$q', '$http', '$location', 'fxCookieService',
		function ($q, $http, $location, fxCookieService) {

			/**
			 * POST to /login URI
			 */
			function loginPost(postData) {

				var deferred = $q.defer();

				$http.post(window.apipath('/login'), postData)
					.success(function (data) {

						// Just make sure there's a field for the message we got back.
						if (!data["login_info"]) {
							data["login_info"] = {};
						}

						// Store the message for persistence.
						data.login_info["message"] = data.login_message;
						var cookieWritten = fxCookieService.tryToStore("login_info", JSON.stringify(data.login_info));

						deferred.resolve({
							fatalError: false,
							loginInProgress: true,
							cookieWritten: cookieWritten,
							data: data
						});

					})
					.error(function (data) {
						deferred.resolve({
							fatalError: true,
							text: 'Failed to sign in!',
							error: true
						});
					});

					return deferred.promise;
			}

			/**
			 * POST to /formdata URI, for remote logins.
			 */
			function loginFormData(postData) {

				var deferred = $q.defer();

				var loginQuery = {
					"method": "remote_control",
					"formData": { 
						"remote_login": {
							"login_data": postData
						}
					},
                    "name": "remote_login",
				};

				$http.post(window.apipath('/formdata'), loginQuery)
					.success(function (data) {

						// Just make sure there's a field for the message we got back.
						if (!data["login_info"]) {
							data["login_info"] = {};
						}

						// Store the message for persistence.
						data.login_info["message"] = data.login_message;
                        var cookie_name = loginInfoName(postData.auth_credentials.objectType,
                                                        postData.auth_credentials.objectID);
						var cookie_written = fxCookieService.tryToStore(cookie_name, JSON.stringify(data.login_info));

						deferred.resolve({
							fatalError: false,
							loginInProgress: data.formData.total_logged_in < data.formData.total_required,
							cookieWritten: cookie_written,
							cookieName: cookie_name,
							data: data
						})
					})
					.error(function(data) {
						deferred.resolve({
							fatalError: true,
							text: "Failed to sign in!",
							error: true
						})
					})

					return deferred.promise;
				};

				function logoutRemote(post_data) {

					var deferred = $q.defer();

					var logoutQuery = {
						"method": "remote_control",
						"formData": {
							"remote_logout": {
								"logout_data": post_data
							}
						},
                        "name": "remote_logout",
					};

					$http.post(window.apipath('/formdata'), logoutQuery)
						.success(function(data) {
							deferred.resolve({
								text: data.formData.message
							});
						})
						.error(function(data) {
							deferred.resolve({
								text: data.formData.message
							});
						});

						return deferred.promise;
				}

            /**
             * Returns the login cookie name
             * @param {string}  objectType  The logged in object Type
             * @param {string}  objectID  The logged in object id
             */
            function loginInfoName(objectType, objectID) {
                var name = 'login_info';
                if (objectType && objectID) {
                    name = [name, objectType, objectID].join('_');
                }

                return name;
            }

			return {
				loginPost: loginPost,
				loginFormData: loginFormData,
                logoutRemote: logoutRemote,
                loginInfoName: loginInfoName
			}
}]);

