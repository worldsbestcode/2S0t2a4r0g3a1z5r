/**
 * The login page single-page app
 */
var fxLogin = angular.module('fxLogin', ['ngAnimate', 'fxCookieUtil', 'fxLoginUtil']);

/**
 * Factory for login http interceptor
 */
fxLogin.factory('expiredLoginInterceptor', ['$q', function($q) {
    var responseInterceptor = {
        response: function(response) {
            return response;
        },
        responseError : function(response) {
            if (response.status === 401) {
                location = '/';
            } else {
                return $q.reject(response);
            }
        }
    };
    return responseInterceptor;
}]);

/**
 * Adds the interceptor to the httpProvider
 */
fxLogin.config(['$httpProvider', '$locationProvider', function($httpProvider, $locationProvider) {
    $httpProvider.interceptors.push('expiredLoginInterceptor');
    $locationProvider.html5Mode({ 
        enabled: true, 
        requireBase: false,
        rewriteLinks: false
    });
}]);

/**
 * The login form
 */
fxLogin.component('loginForm', {
    templateUrl: 'components/sections/login/loginForm.html',
    bindings: {
        objectId: '=',
        objectParentId: '=',
        objectType: '=',
        loginContextString: '=',
        setAuthorizedIds: '=',
        guardianLogin: '@',
    },
	controller: ['$scope', '$http', '$location', 'fxCookieService', 'fxLoginService',	
		function ($scope, $http, $location, fxCookieService, fxLoginService) {
            $scope.bindings = this;
            $scope.guardianLogin = $scope.bindings.guardianLogin;

			$scope.previousLoginReponse = fxCookieService.getPreviousLoginInfo($scope.bindings.objectID);
			$scope.loginInProgress = $scope.previousLoginReponse != "";

			if (!$scope.loginInProgress) {
				$scope.previousLoginReponse = "";
			}

			$scope.loginMessage = {
				text: $scope.previousLoginReponse,
				error: false
			};

			$scope.userRoles = {
				pendingGroups: [],
				authorizedGroups: []
			};

			$scope.authDispNames = ['Username/Password'];
			$scope.authTypeName = $scope.authDispNames[0];

			$scope.username = '';
			$scope.password = '';
			$scope.uniqueID = $location.search().uniqueID;

			$scope.cookiesEnabled = fxCookieService.hasCookiesEnabled();
			if (!$scope.cookiesEnabled) {
				$scope.loginMessage.error = true;
				$scope.loginMessage.text = 'Please enable cookies to continue!';
			}

			/**
			 * Displays the sign in message
			 */
			$scope.signInStep = function (loginMessage) {
				$scope.loginMessage = loginMessage;
				$scope.username = $scope.password = '';
				angular.element('#usernameInput').focus();
            };
            
			/**
			* Attempt to sign in.
			*/
			$scope.signIn = function (authTypeName, fields) {

                $scope.isMainLogin = true;

                if ($scope.bindings.objectId || $scope.bindings.objectParentId) {
                    $scope.isMainLogin = false;
                }

                var post_data = {};

				// Username/password
				if (authTypeName === $scope.authDispNames[0]) {
                    
                    if ($scope.isMainLogin) {
                        post_data = {
                            auth_type: 'userpass',
                            auth_credentials: {
                                username: $scope.username,
                                password: $scope.password
                            }
                        };
                    } else {
                        post_data = {
							auth_type: "userpass", 
                            auth_credentials: {
                                username: $scope.username,
                                password: $scope.password,
                                objectID: $scope.bindings.objectId,
                                objectParentID: $scope.bindings.objectParentId,
                                objectType: $scope.bindings.objectType
                            }
                        };
                    }

					if ($scope.uniqueID != null) {
						post_data["uniqueID"] = $scope.uniqueID;
					}
				}

				// Anonymous
				else if (authTypeName === $scope.authDispNames[1]) {
					post_data = {
						auth_type: 'anonymous'
					};

					if ($scope.uniqueID != null) {
						post_data["uniqueID"] = $scope.uniqueID;
					}
				}

				else {
					$scope.loginMessage = {
						text: 'Invalid authentication type!',
						error: true
					};
                }
                
                if (post_data !== {}) {
                    // Merge in any pre-determined fields to "post_data"
                    if (fields) {
                        Object.keys(fields).map(function(fieldName) {
                            post_data[fieldName] = fields[fieldName];
                        });
                    }

                    // Determine how to login
                    if ($scope.isMainLogin) {
					    fxLoginService.loginPost(post_data).then(function(ret_data) {
                           $scope.finishLogin(ret_data);
                       });
                    } else {
                        fxLoginService.loginFormData(post_data).then(function(ret_data) {
                            $scope.finishRemoteLogin(ret_data);
                        });
                    }
                }
            };

            $scope.loginNow = function() {
                $scope.signIn($scope.authTypeName, {
                    login_now: true
                });
            };

            /**
             * Finish the login process.
             */
            $scope.finishLogin = function (ret_data) {
                
                $scope.loginInProgress = ret_data.loginInProgress;
                $scope.userRoles.pendingGroups = ret_data.data.pending_groups ? ret_data.data.pending_groups : [];
                $scope.userRoles.authorizedGroups = ret_data.data.authorized_groups ? ret_data.data.authorized_groups : [];

                if (ret_data.fatalError === false) {
                    // Fully logged in
                    // (result is exactly boolean true)
                    if (ret_data.data.result === true) {
                        if (ret_data.cookieWritten) {
                            if ($scope.uniqueID) {
                                window.location = '/regauth/download?uniqueID=' + $scope.uniqueID;
                            } else {
                                window.location = '/';
                            }
                            fxCookieService.clearPreviousLoginMessage();
                        }
                        else {
                            window.alert('Please enable cookies to continue!');
                        }

                    }
                    // Partial login
                    // (result value is anything else)
                    else {
                        $scope.signInStep({
                            text: ret_data.data.login_message,
                            error: false
                        });
                    }
                } else {
                    $scope.signInStep({
                        text: ret_data.text,
                        error: true
                    });
                }
            };
             
            /**
             * Finish the login process but for remotes.
             */
            $scope.finishRemoteLogin = function (ret_data) {
                
                $scope.loginInProgress = ret_data.loginInProgress;
                $scope.userRoles.pendingGroups = ret_data.data.formData.pending_groups ? ret_data.data.formData.pending_groups : [];
                $scope.userRoles.authorizedGroups = ret_data.data.formData.authorized_groups ? ret_data.data.formData.authorized_groups : [];
                
                if (ret_data.fatalError === false) {

                    $scope.signInStep({
                        text: ret_data.data.formData.login_message,
                        error: false
                    });

                    if (ret_data.data.formData.result === true) {

                        if (ret_data.cookieWritten) {
                            fxCookieService.clearPreviousLoginMessage(ret_data.cookieName);
                        } else {
                            window.alert('Please enable cookies to continue!');
                        }

                    }
                } else {
                    $scope.signInStep({
                        text: ret_data.text,
                        error: true
                    });
                }

                $scope.bindings.setAuthorizedIds(fxCookieService.getAuthorizedRemoteObjectIDs());
            };

			/**
			 * Clear the previous login message when we click Cancel.
			 */
			$scope.cancelLogin = function () {

                if ($scope.bindings.objectId || $scope.bindings.objectParentId) {
                    var cookie_name = fxLoginService.loginInfoName($scope.bindings.objectType,
                                                                   $scope.bindings.objectId);

                    fxCookieService.clearPreviousLoginMessage(cookie_name);

                    post_data = {
                        objectID: $scope.bindings.objectId,
                        objectParentID: $scope.bindings.objectParentId,
                        objectType: $scope.bindings.objectType
                    };

                    fxLoginService.logoutRemote(post_data).then(function (ret_data) {
                        $scope.signInStep({
                            text: ret_data.text,
                            error: false
                        });

                        $scope.loginInProgress = false;

                        $scope.bindings.setAuthorizedIds(fxCookieService.getAuthorizedRemoteObjectIDs());
                    });

                } else {
                    fxCookieService.clearPreviousLoginMessage();
                    window.location = '/logout';
                }
			};
		}]
});
