/**
 * The base HTML of the CSR view
 */
fxApp.component('csrView', {
	templateUrl: 'components/sections/csrView/content.html'
});

/**
 * Shown when nothing is selected
 */
fxApp.component('placeholder', {
	templateUrl: 'components/sections/csrView/placeholder.html',
	controller: ['$scope', '$q', 'fxAppService', 'fxAppTreeService', 'csrViewService',
		function($scope, $q, fxAppService, fxAppTreeService, csrViewService) {

		// View switching info
		$scope.views = fxAppService.getViews();
		$scope.viewDisplayed = fxAppService.getView();
		$scope.isAnonymous = fxAppService.isAnonymous();

        /**
         * Function to get the associated count type
         * @param countType  The signing approval object type
         * @return The selected count type if it exists for our view or else the filterCount
         */
        $scope.getTypeCount = function (countType) {
            if ($scope.filterCount.hasOwnProperty(countType)) {
                return $scope.filterCount[countType];
            } else {
                return fxAppTreeService.paginationData.filterCount;
            }
        }

        var pendingCount = null;

        // Get pending, signed, and denied counts if using "csrViewAll"
        if ($scope.viewDisplayed === $scope.views['csrViewAll']) {
            pendingCount = csrViewService.getPendingSignedDeniedCounts().then(function (counts) {
                return {
                    pending: counts.pending,
                    signed: counts.signed,
                    denied: counts.denied
                };
            });
        } else {
            // Uses an empty object to fall back to the filter count otherwise
            pendingCount = $q.resolve({});
        }

		// Get total count
		csrViewService.getApprovableObjectTotalCount().then(function(count) {
            // Set all our counts at the same time
            pendingCount.then(function (typeCounts) {
                $scope.totalCount = count;
                $scope.filterCount = typeCounts;
            });
		});
	}]
});

/**
 * Shown when a cert request is selected from the tree
 */
fxApp.component('csrForm', {
	templateUrl: 'components/sections/csrView/csrForm.html',
	bindings: {
		logindata:     '=',
		formdata:      '<',
		approve:       '=',
		deny:          '=',
		renew:         '=',
		save:          '=',
		downloadcert:  '=',
        downloadcrl:   '=',
		csrupload:     '=',
        remove:        '=',
        revoke:        '=',
		injectintosmarttoken: '='
	},
	controller: ['$scope', 'csrViewService', 'fxAppService', 'downloadViewService', 'fxAppModalService', 
                function($scope, csrViewService, fxAppService, downloadViewService, fxAppModalService) {
		$scope.csrViewService = csrViewService;
		$scope.fxAppService = fxAppService;
		// when in approval mode, the update button
		// is swapped with the approve/deny buttons
		$scope.approvalMode = false;

        /**
         * Grab the form data
         * @return {object}  The formdata from the scope
         */
        function getData () {
            return $scope.$ctrl.formdata;
        }

		/**
		 * Enables approval mode when the "Signing Approvals" tab is clicked
		 */
		$scope.setApprovalMode = function() {
			$scope.approvalMode = true;
		};

		/**
		 * Disables approval mode when the "Signing Approvals" tab is inactive
		 */
		$scope.resetApprovalMode = function() {
			$scope.approvalMode = false;
			
			var formdata = getData();
			formdata.profileOverride = false;
		};

		$scope.setProfileOverride = function() {
            var formdata = getData();
			formdata.profileOverride = true;
		};

        $scope.canDownload = function () {
            var formdata = getData();
            return (formdata.signedCert && formdata.signedCert.length) ||
                (formdata.signature && formdata.signature.length);
        }

        $scope.isHash = function () {
            return csrViewService.isHash(getData());
        };

        $scope.hasCrl = function () {
            return getData().certCrl && getData().certCrl.crlData;
        };

        $scope.isCSR = function () {
            return csrViewService.isCSR(getData());
        };

        $scope.isVetter = function () {
            return fxAppService.getLoginData().permissions.vetter === true;
        };

		$scope.renewDisabled = function() {
			var data = getData();
			if (!data.issuancePolicyData.allowRenewal || data.status.toLowerCase() !== 'signed') {
				return 'true';
			} else {
				return null;
			}
		};

        $scope.fieldDisabled = function (ignoreMultipleApprovals) {
			if (ignoreMultipleApprovals !== true) {
				ignoreMultipleApprovals = false;
			}

            var perms = fxAppService.getLoginData().permissions;
            return csrViewService.permissionsShouldDisableField(getData(), perms, ignoreMultipleApprovals);
		};
		
		$scope.canEdit = function (ignoreMultipleApprovals) {
			if (ignoreMultipleApprovals !== true) {
				ignoreMultipleApprovals = false;
			}

            return $scope.fieldDisabled(ignoreMultipleApprovals) === null;
		};
		
        $scope.isHashEnabled = function() {
            return $scope.canEdit() && $scope.isCSR();
        };

        /**
         * True if the object can be revoked
         */
        $scope.canRevoke = function () {
            return getData().status.toLowerCase() === 'signed' &&
                $scope.isVetter() &&
                $scope.isCSR();
        }

        /**
         * Check if the current user uploaded the current item
         * Returns: {boolean}  True if uploader and not anonymous
         */
        function isUploader() {
            // The anonymous identity can't own things
            if (fxAppService.isAnonymous()) {
                return false;
            }

            var users = fxAppService.getLoginData().users;
            for (var i = 0; i < users.length; i++) {
                if (users[i].id === getData().uploaderId) {
                    return true;
                }
            }

            return false;
        }

        /**
         * True if the user can delete the item
         */
        $scope.canDelete = function () {
            return $scope.canEdit() || $scope.isVetter() || isUploader();
        }

        $scope.pkcs12RequiresPassword = function() {
            var formdata = getData();
            return formdata.downloadTypeSelected === 'DER (PKCS #12)' && 
                   formdata.pkcs12.length === 0;
        }
        
       $scope.downloadPKCS12 = function() {
            var formdata = getData();
            downloadViewService.getDownload(
                formdata.uniqueID,
                formdata.password,
                formdata.clear_pki
            ).then(function(data) {
                if (data.result === "Failure") {
                    fxAppModalService.showModal('Error', data.message);
                }
                else {
                    // Download the file
                    downloadViewService.downloadString(
                        downloadViewService.hexToArrayBuffer(data.pki),
                        downloadViewService.spacesToUnderscores(data.name) + '_pkcs12.der');
                    
                    var formdata = getData();
                    formdata.pkcs12 = data.pki;
                }
            });
       }

	}]
});

/**
 * The CSR view controller
 */
var csrViewCtrl = fxApp.controller('csrViewCtrl',
	['$scope', '$rootScope', '$http', '$q', 'fxAppService', 'csrViewService', 'fxAppX509Service',
		'fxAppTreeService', 'fxAppModalService', 'fxAppFilterService', '$timeout',
	function($scope, $rootScope, $http, $q, fxAppService, csrViewService, fxAppX509Service,
		fxAppTreeService, fxAppModalService, fxAppFilterService, $timeout) {

	$scope.fxAppService = fxAppService;
	$scope.csrViewService = csrViewService;
	$scope.fxAppTreeService = fxAppTreeService;
	$scope.fxAppFilterService = fxAppFilterService;

	// Set filter options
	csrViewService.setupFilter($scope);

	// Define forms for the CSR view
	$scope.forms = {
		placeholder: 0,
		csrForm:     1
	};

	// Set the initial form displayed
	$scope.formToDisplay = $scope.forms['placeholder'];

	// Filter results that populate the tree
	$scope.approvalGroups = [];
	$scope.certRequestsFromFilter = [];

	// Register pagination callbacks
	fxAppTreeService.next = function() {
		fxAppTreeService.paginationData.currentPage += 1;
		csrViewService.getTreeForView($scope);
		$scope.formToDisplay = $scope.forms['placeholder'];
	};

	fxAppTreeService.prev = function() {
		fxAppTreeService.paginationData.currentPage -= 1;
		csrViewService.getTreeForView($scope);
		$scope.formToDisplay = $scope.forms['placeholder'];
	};

	// Perform a filter query for the current view
	csrViewService.getTreeForView($scope);

	// Update the tree and form on view change
	var viewChangeTreeUpdate = $rootScope.$on('viewChange',function() {
		var viewDisplayed = fxAppService.getView();
		var views = fxAppService.getViews();

		// Check what view the user is in
		if (viewDisplayed >= views['csrViewPending'] &&
			viewDisplayed <= views['csrViewFilter']) {

			// Reset filter page
			fxAppTreeService.resetPage();

			// Get tree for every csr view except filter
			if (viewDisplayed !== views['csrViewFilter']) {
				csrViewService.getTreeForView($scope);

				// Register pagination callbacks
				fxAppTreeService.next = function() {
					fxAppTreeService.paginationData.currentPage += 1;
					csrViewService.getTreeForView($scope);
					$scope.formToDisplay = $scope.forms['placeholder'];
				};

				fxAppTreeService.prev = function() {
					fxAppTreeService.paginationData.currentPage -= 1;
					csrViewService.getTreeForView($scope);
					$scope.formToDisplay = $scope.forms['placeholder'];
				};
			}

			// Show placeholder for all csr views
			$scope.formToDisplay = $scope.forms['placeholder'];
		}

		// Cancel this event handler if user left the CSR view
		else {
			viewChangeTreeUpdate();
		}
	});

	// FORMS
	$scope.fxForms = this;
	$scope.fxForms.csrForm = { 
		data: {},

		/**
		 * Called when "Approve" button is clicked
		 */
		approveCallback: function() {
			var csr = csrViewService.prepareCsr($scope.fxForms.csrForm.data);
			
			// default modal message
			var alertTitle = "Validation Failed";
			var alertMessage = "CSR approval failed.";

			csrViewService.validateCsr(csr).then(function(data) {

				csrViewService.updateCsr(
					csr,
					'Approved',
					$scope.fxForms.csrForm.data.signingApprovalMessage
				).then(function (data) {

					if (data.objectData.message) {
						alertTitle = data.objectData.result ? 'Message' : 'Error';
						alertMessage = data.objectData.message;
					}
					else {
						if (data.objectData.result) {
							alertTitle = 'Message';
							alertMessage = 'Signing request has been successfully approved!';

							// store the state of the tree, but do not track the child
							// because it won't be available after approvalGroups changes
							$scope.treePrevState = csrViewService.createTreeState($scope.treeControl, false);
						}
						else {
							alertTitle = 'Error';
							alertMessage = 'Failed to approve signing request!';
						}
					}

					fxAppModalService.showModal(alertTitle, alertMessage, function (event) {
						// Update tree with modal dismiss
						if (data.objectData.result) {
							csrViewService.getTreeForView($scope);
						}
					});
				});
			}, function (data) {
				fxAppModalService.showModal('Error', data.objectData.message ? data.objectData.message : alertMessage);
			});
		},

		/**
		 * Called when "Deny" button is clicked
		 */
		denyCallback: function() {
			var csr = csrViewService.prepareCsr($scope.fxForms.csrForm.data);
				
			// default modal message
			var alertTitle = "Validation Failed";
			var alertMessage = "CSR deny failed.";

			csrViewService.validateCsr(csr).then(function (data) {

				csrViewService.updateCsr(
					csr,
					'Denied',
					$scope.fxForms.csrForm.data.signingApprovalMessage
				).then(function (data) {
					if (data.objectData.message) {
						alertTitle = data.objectData.result ? 'Message' : 'Error';
						alertMessage = data.objectData.message;
					}
					else {
						if (data.objectData.result) {
							alertTitle = 'Message';
							alertMessage = 'Signing request has been successfully denied!';

							// store the state of the tree, but do not track the child
							// because it won't be available after approvalGroups changes
							$scope.treePrevState = csrViewService.createTreeState($scope.treeControl, false);
						}
						else {
							alertTitle = 'Error';
							alertMessage = 'Failed to deny signing request!';
						}
					}

					fxAppModalService.showModal(alertTitle, alertMessage, function (event) {
						// Update tree with modal dismiss
						if (data.objectData.result) {
							csrViewService.getTreeForView($scope);
						}
					});
				});
			}, function (data) {
				fxAppModalService.showModal('Error', data.objectData.message ? data.objectData.message : alertMessage);
			});
		},

		/**
		 * Called when "Renew" button is clicked
		 */
		renewCallback: function() {
			var csr = csrViewService.prepareCsr($scope.fxForms.csrForm.data);

			// default modal message
			var alertTitle = "Validation Failed";
			var alertMessage = "CSR validation failed."

			csrViewService.validateCsr(csr).then(function (data) {

				csrViewService.renewCsr(
					csr
				).then(function (data) {

					if (data.objectData.message) {
						alertTitle = data.objectData.result ? 'Message' : 'Error';
						alertMessage = data.objectData.message;
					}
					else {
						if (data.objectData.result) {
							alertTitle = 'Message';
							alertMessage = 'Signing request has been successfully renewed!';

							// store the state of the tree, but do not track the child
							// because it won't be available after approvalGroups changes
							$scope.treePrevState = csrViewService.createTreeState($scope.treeControl, false);
						}
						else {
							alertTitle = 'Error';
							alertMessage = 'Failed to renew signing request!';
						}
					}

					fxAppModalService.showModal(alertTitle, alertMessage, function (event) {
						// Update tree with modal dismiss
						if (data.objectData.result) {
							csrViewService.getTreeForView($scope);
						}
					});
				});
			}, function (data) {
				fxAppModalService.showModal('Error', data.objectData.message ? data.objectData.message : alertMessage);
			});
		},

		downloadCertCallback: function() {
            var downloadType = $scope.fxForms.csrForm.data.downloadTypeSelected;
            var fileData = false;
            var filename = csrViewService.spacesToUnderscores($scope.fxForms.csrForm.data.name);
            if (downloadType === "PEM (X.509)") {
                fileData = $scope.fxForms.csrForm.data.signedCertPEM;
                filename += '_x509.pem';
            } else if (downloadType === "DER (X.509)") {
                fileData = csrViewService.hexToArrayBuffer($scope.fxForms.csrForm.data.signedCert);
                filename += '_x509.der';
            } else if (downloadType === "DER (PKCS #7)") {
                fileData = csrViewService.hexToArrayBuffer($scope.fxForms.csrForm.data.signedCertPKCS7);
                filename += '_pkcs7.der';
            } else if (downloadType === "DER (PKCS #12)") {
                fileData = csrViewService.hexToArrayBuffer($scope.fxForms.csrForm.data.pkcs12);
                filename += '_pkcs12.der';
            } else if (downloadType === 'Hexadecimal') {
                fileData = $scope.fxForms.csrForm.data.signature;
                filename += '.hex';
            } else if (downloadType === 'Binary') {
                fileData = csrViewService.hexToArrayBuffer($scope.fxForms.csrForm.data.signature);
                filename += '.sig';
            }

            if (fileData) {
                csrViewService.downloadString(fileData, filename);
            }
		},
        downloadCrlCallback: function () {
            var data = $scope.fxForms.csrForm.data;
            var crl = data.certCrl;
            var downloadType = data.downloadTypeSelected;

            var filename = csrViewService.spacesToUnderscores(data.signingCertName);
            var fileData = false;
            if (downloadType === 'DER (X.509)') {
                fileData = csrViewService.hexToArrayBuffer(crl.crlData);
                filename += '_der.crl';
            } else if (downloadType === 'PEM (X.509)') {
                fileData = fxAppX509Service.pemEncode('X509 CRL', crl.crlData);
                filename += '_pem.crl';
            }

            if (fileData) {
                csrViewService.downloadString(fileData, filename);
            }
        },
        removeCallback: function () {
            var formdata = $scope.fxForms.csrForm.data

            /**
             * Sends the message to the server after confirmation
             */
            function serverRemove() {
                if (fxAppModalService.getResponse() !== 'OK') {
                    // Do nothing if the modal was dismissed for another reason
                    return;
                }

                var message = {objectData: {}};
                message.objectData[formdata.objectType] = [formdata.objectID]

                var config = {
                    data: message,
                    headers: {'Content-Type': 'application/json'}
                };

                $http.delete(window.apipath('/object'), config).then(function (response) {
                    dataResult = response
                    if (response.data.result === 'Success') {
                        $scope.formToDisplay = $scope.forms.placeholder;
                        csrViewService.getTreeForView($scope);
                    } else {
                        fxAppModalService.showModal('Error', response.message)
                    }
                });
            }

            var modal = {
                title: 'Confirm Deletion',
                message: 'Delete request ' + formdata.name + '?',
                options: {
                    showCancelButton: true,
                    customButtons: [],
                    response: ''
                }
            }

            // Make sure the deletion is intentional
            fxAppModalService.showModal(modal.title, modal.message, serverRemove, modal.options);
        },
        revokeCallback: function () {
            var data = $scope.fxForms.csrForm.data;
            var message = {
                method: 'revoke',
                revokeData: {
                    ids: [data.objectID],
                    reason: data.revokeReason,
                    notes: data.revokeNotes
                }
            };

            $http.post(window.apipath('/approve'), message).success(function (data) {
                var modal = {
                    title: 'Message',
                    message: 'CSR has been successfully revoked',
                    callback: function (event) {
                        csrViewService.getTreeForView($scope);
                    }
                };

                if (data.objectData.result !== true) {
                    modal = {
                        title: 'Error',
                        message: data.objectData.message ? data.objectData.message : 'No response from server',
                        callback: angular.noop
                    };
                }

                fxAppModalService.showModal(modal.title, modal.message, modal.callback);
            });
        },
		/**
		 * Called when "Update" button is clicked
		 */
		saveCallback: function() {
			var csr = csrViewService.prepareCsr($scope.fxForms.csrForm.data);

			// Default modal info
			var modalInfo = {
				title: 'Validation Failed',
				message: '',
				callback: function() {}
			};

			// Client-side validation
			csrViewService.clientValidateCsr(csr).then(function() {
				// Client-side validation passed
				return $q.resolve();
			}, function(message) {
				// Client-side validation failed
				modalInfo.message = message;
				return $q.reject();
			}).then(function() {
				var deferred = $q.defer();

				// Server-side validation
				csrViewService.validateCsr(csr).then(function(data) {
					// Server-side validation passed
					modalInfo.message = data.objectData.message;
					deferred.resolve();
				}, function(data) {
					// Server-side validation failed
					modalInfo.message = data.objectData.message;
					deferred.reject();
				});

				return deferred.promise;
			}).then(function() {
				var deferred = $q.defer();

				// Update the CSR
				csrViewService.updateCsr(csr, '', '').then(function(data) {
					if (data.result === 'Success') {
						modalInfo.title = 'Message';
						modalInfo.message = 'Signing request has been successfully updated.';

						// Store the state of the tree
						$scope.treePrevState = csrViewService.createTreeState($scope.treeControl, true);
					}
					else {
						modalInfo.title = 'Error';
						modalInfo.message = 'Failed to update signing request!';
					}

					modalInfo.callback = function(event) {
						// Update tree with modal dismiss if update succeeded
						if (data.result === 'Success') {
							csrViewService.getTreeForView($scope);
						}
					};

					deferred.resolve();
				});

				return deferred.promise;
			}).finally(function() {
				fxAppModalService.showModal(modalInfo.title, modalInfo.message, modalInfo.callback);
			});
		},

		/**
		 * Called when a request is uploaded to parse it server-side
		 *
		 * @param {string}    filestring - hex-encoded file
		 */
		csrUploadCallback: function(filestring) {
			csrViewService.getFormDataFromUploadedCsr(filestring).then(function(data) {
				if (data) {
					$scope.fxForms.csrForm.data.subject = data.subject ? csrViewService.subjectParse(data.subject) : "";
					$scope.fxForms.csrForm.data.hash = data.hash ? data.hash : "";
					$scope.fxForms.csrForm.data.keyType = data.keyType ? data.keyType : "";
					$scope.fxForms.csrForm.data.request = data.request ? data.request : "";
					$scope.fxForms.csrForm.data.token_key_name = data.token_key_name ? data.token_key_name : "";
					$scope.fxForms.csrForm.data.token_provider_name = data.token_provider_name ? data.token_provider_name : "";
				}
			});
		}
	};


	// for temporarily disabling watch events
	$scope.stopPropagate = {
		keyTypeSelected: false
	};

	// called when the extension profile is selected
	$scope.$watch('fxForms.csrForm.data.extensionProfile', function() {
        if ($scope.fxForms.csrForm.data.signingCert) {
			csrViewService.getProfileExtensionSet(
				$scope.fxForms.csrForm.data.extensionProfile,
                $scope.fxForms.csrForm.data.signingCert
			).then(function(data) {
				$scope.fxForms.csrForm.data.v3Extensions = data.extensions;
				$scope.fxForms.csrForm.data.extensionProfileData = data.profile;
			});
		}
	});

	// called every time the extension data is changed by the user
	$scope.$watch('fxForms.csrForm.data.v3Extensions', function() {
		if ($scope.fxForms.csrForm.data.v3Extensions &&
			typeof $scope.fxForms.csrForm.data.v3Extensions === 'object') {
			csrViewService.updateExtensionValues($scope.fxForms.csrForm.data.v3Extensions);
		}
	}, true);

	// called every time the extension options change
	$scope.$watch('fxForms.csrForm.data.v3ExtOptions', function() {
		// Sort the options
		if ($scope.fxForms.csrForm.data.v3ExtOptions) {
			$scope.fxForms.csrForm.data.selectedExtension = csrViewService.sortExtOptions(
				$scope.fxForms.csrForm.data.v3ExtOptions
			);

			$scope.fxForms.csrForm.data.v3ExtOptions = csrViewService.removeDuplicateOptions(
				$scope.fxForms.csrForm.data.v3ExtOptions,
				$scope.fxForms.csrForm.data.v3Extensions
			);
		}
	}, true);

	// called when the key type is selected
	$scope.$watch('fxForms.csrForm.data.keyTypeSelected', function(newValue, oldValue) {
		if ($scope.fxForms.csrForm.data.isGeneratedPKI && !$scope.stopPropagate.keyTypeSelected) {
			if (newValue) {
				var selectedKey = csrViewService.getObjKeys(newValue)[0];

				$scope.fxForms.csrForm.data.keyTypeSelectedSize = csrViewService.determineInitialKeyTypeValue(
					csrViewService.getFirstInnerValue(newValue),
					csrViewService.keyTypeDefs().defaultSizes[selectedKey]
				);
			}
		}

		// reset stopPropagate
		$scope.stopPropagate.keyTypeSelected = false;
	});

	// TREE VIEW
	// initial data for tree
	$scope.treeData = $scope.fxAppTreeService.treeData;
	$scope.treeControl = $scope.fxAppTreeService.treeControl;
	$scope.treePrevState = {};
	$scope.dummyLabel = 'loading...';

	$scope.$watch('treeData', function() {
		$scope.fxAppTreeService.treeData = $scope.treeData;
	});

	$scope.$watch('fxAppTreeService.treeControl', function() {
		$scope.treeControl = $scope.fxAppTreeService.treeControl;
	});

	// called when approvalGroups changes
	$scope.$watch('approvalGroups',function() {
		if ($scope.approvalGroups) {

			// set the tree data
			$scope.treeData = $scope.approvalGroups.map(function(item) {
				return {
					label: item.name,
					children: [{ label: $scope.dummyLabel, visible: false }],
					value: item
				};
			});

			// set the tree data from filter results
			if ($scope.certRequestsFromFilter.length) {
				// set the cert requests per approval group
				$scope.certRequestsFromFilter.map(function(certRequest) {
					$scope.treeData = $scope.treeData.map(function(parent) {
						if (parent.value.objectID === certRequest.parentID) {
							// Remove dummy children
							if (!parent.children[0].value) {
								parent.children.pop();
							}

							parent.children.push({
								label: certRequest.name,
								value: certRequest
							});
						}

						return parent;
					});
				});
				$scope.certRequestsFromFilter = [];
			}

			// check if tree is ready
			if (Object.keys($scope.treeControl).length) {
				$scope.treeWhenReady();
			}
		}

		// display placeholder when last CSR is approved/denied
		if($scope.approvalGroups && $scope.approvalGroups.length === 0) {
			$scope.formToDisplay = $scope.forms['placeholder'];
		}
	});

	/**
	 * Called when a tree branch is selected
	 */
	$scope.treeSelectEvent = function() {
        var selectedBranch = $scope.treeControl.get_selected_branch();
        /**
         * Used by object and csr requests to fill out the approval table
         */
        var filloutApprovalTable = function () {
            var data = $scope.fxForms.csrForm.data;
            if (typeof data.signingApprovals[0] === 'string') {
                data.signingApprovals = data.signingApprovals.map(function(item) {
                    return JSON.parse(item);
                });
            }
        };

        var branchEvent = {
            APPROVAL_GROUP: function() {
				// can only have one branch expanded at a time
				csrViewService.selectBranch($scope.treeControl, {
					branch: selectedBranch,
					options:['collapse_all', 'expand_branch']
				});
            },
            CERT_REQ: function() {
				// populate csrForm with data
				$scope.fxForms.csrForm.data = selectedBranch.value;
                $scope.fxForms.csrForm.data.password = "";
                $scope.fxForms.csrForm.data.clear_pki = false;

				// loading...
				fxAppService.setLoading();

				// fetch the signing cert and issuance policy for this cert requests
                csrViewService.getIssuancePolicies('CERT_REQ', [$scope.fxForms.csrForm.data.objectID]).then(function(policies) {
                    // assign the signing cert and issuance policy data
					$scope.fxForms.csrForm.data.issuancePolicyData = policies[0];
					
                    // set additional form data
                    csrViewService.getProfileExtensionSet(
                        $scope.fxForms.csrForm.data.extensionProfile,
                        $scope.fxForms.csrForm.data.signingCert
                    ).then(function(data) {
                        $scope.fxForms.csrForm.data.extensionProfileData = data.profile;
                        $scope.fxForms.csrForm.data.v3ExtOptions = csrViewService.getAllExtensions();
                        $scope.fxForms.csrForm.data.v3Extensions = data.extensions;
                    });
					
					csrViewService.getCertExtensionSet(
                        $scope.fxForms.csrForm.data.objectID
                    ).then(function(data) {
                        $scope.fxForms.csrForm.data.v3CertExtensions = data.extensions;
                    });

                    // DN profiles
                    csrViewService.getDNProfilesAsFormData(['None', 'Classic']).then(function(profiles) {
                        $scope.fxForms.csrForm.data.DNProfiles = profiles;
                        $scope.fxForms.csrForm.data.selectedDNProfile = profiles[0];
                    });

                    // signing approval table
                    filloutApprovalTable();

                    // selected key type
                    var keyTypeParams = csrViewService.keyTypeStringToFormParams(
                        $scope.fxForms.csrForm.data.keyType,
                        $scope.fxForms.csrForm.data.issuancePolicyData.keyTypes
                    );
                    $scope.fxForms.csrForm.data.keyTypeSelected = keyTypeParams.keyTypeSelected;
                    $scope.fxForms.csrForm.data.keyTypeSelectedSize = keyTypeParams.keyTypeSelectedSize;
                    $scope.stopPropagate.keyTypeSelected = true;

                    // download type
                    $scope.fxForms.csrForm.data.downloadTypes = ['PEM (X.509)', 'DER (X.509)', 'DER (PKCS #7)', 'DER (PKCS #12)'];
                    $scope.fxForms.csrForm.data.downloadTypeSelected = $scope.fxForms.csrForm.data.downloadTypes[0];

                    // display csrForm
                    $scope.formToDisplay = $scope.forms['csrForm'];
                    fxAppService.resetLoading();
                }).then(function queryCRL() {
                    var data =  $scope.fxForms.csrForm.data;
                    csrViewService.setCrlFromCertificate(data.signingCertCrl, data);
                });
            },
            SIGNABLE_OBJ: function() {
                $scope.fxForms.csrForm.data = selectedBranch.value;
                var data = $scope.fxForms.csrForm.data;
                fxAppService.setLoading();
                csrViewService.getIssuancePolicies('SIGNABLE_OBJ', [data.objectID]).then(function(policies) {
                    data.issuancePolicyData = policies[0];
                    data.issuancePolicyData.paddingModes = data.issuancePolicyData.paddingModes.split(',');

                    filloutApprovalTable();
                    data.downloadTypes = ['Binary', 'Hexadecimal'];
                    data.downloadTypeSelected = data.downloadTypes[0];

                    $scope.formToDisplay = $scope.forms['csrForm'];
                    fxAppService.resetLoading();
                });


            }
        };

        var objectType = false;
        if (selectedBranch && selectedBranch.value) {
            objectType = selectedBranch.value.objectType;
        }

        // branch is still selected
        if (objectType && branchEvent[objectType]) {
            branchEvent[objectType]();
        } else {
            // display placeholder
            $scope.formToDisplay = $scope.forms['placeholder'];
        }
	};

	/**
	 * Called when the tree has finished loading
	 */
	$scope.treeWhenReady = function() {
		// clear selected branch and collapse all
		csrViewService.selectBranch($scope.treeControl, {
			options:['expand_all']
		});
	};

	/**
	 * Called when the internal tree data has changed (including selection)
	 */
	$scope.treeOnChanged = function() {
		var selected = $scope.treeControl.get_selected_branch();

		// nothing in the tree is currently selected
		if (!selected) {

			$scope.treeControl.expand_all();

			// something in the tree was previously selected
			if (Object.keys($scope.treePrevState).length) {

				// select parent branch
				if ($scope.treePrevState.parentLabel) {
					var parentBranch = findByLabel($scope.treePrevState.parentLabel, $scope.treeData);

					// found parent
					if (parentBranch) {

						// select previously selected parent branch
						csrViewService.selectBranch($scope.treeControl, {
							branch: parentBranch,
							options:['expand_all']
						});

						// clear previous parent
						$scope.treePrevState.parentLabel = undefined;
					}

					// could not find parent
					else {

						// display placeholder
						$scope.formToDisplay = $scope.forms['placeholder'];

						// clear previous state
						$scope.treePrevState = {};
					}
				}
			}
		}

		// something in the tree is currently selected
		else {

			// something in the tree was previously selected
			if (Object.keys($scope.treePrevState).length) {

				// select the child branch once the parent branch has children
				if ($scope.treePrevState.childLabel &&
					selected.children.length &&
					selected.children[0].label !== $scope.dummyLabel) {

					var childBranch = findByLabel($scope.treePrevState.childLabel, selected.children);

					// found child
					if (childBranch) {

						// select previously selected child branch
						csrViewService.selectBranch($scope.treeControl, {
							branch: childBranch
						});

						// display csrForm
						$scope.formToDisplay = $scope.forms['csrForm'];
					}

					// clear previous state
					$scope.treePrevState = {};
				}
			}
		}

		function findByLabel(label, items) {
			return items.filter(function(item) {
				return item.label === label;
			})[0];
		}
	};

	$scope.treeDetermineIcon = function(branch) {
		switch (branch.value.status) {
			case 'Pending':
				return 'fa fa-clock-o light-blue-text';
			case 'Signed':
				return 'fa fa-check-circle green-text';
			case 'Denied':
				return 'fa fa-times-circle red-text';
			default:
				return 'fa fa-file';
		}
	};

	$scope.fxAppTreeService.treeSelectEvent = $scope.treeSelectEvent;
	$scope.fxAppTreeService.treeWhenReady = $scope.treeWhenReady;
	$scope.fxAppTreeService.treeOnChanged = $scope.treeOnChanged;
	$scope.fxAppTreeService.treeDetermineIcon = $scope.treeDetermineIcon;

	// FILTER
	// filter callback
	fxAppFilterService.setCallback(function(clauses, modalDoneCallback) {

		function getTreeForFilter() {
			// loading...
			fxAppService.setLoading();

			// get tree data
			csrViewService.getTreeForView($scope, clauses.map(function(clause) {
				return clause.values;
			}), modalDoneCallback);
		}

		// Register callback for updating when next/prev clicked
		fxAppTreeService.updateTree = function() {
			getTreeForFilter();
			$scope.formToDisplay = $scope.forms['placeholder'];
		};

		// populate tree
		getTreeForFilter();

		// switch to filter results view
		fxAppService.setView(fxAppService.getViews()['csrViewFilter']);
	});

	// export callback
	fxAppFilterService.exportResults = function() {
		fxAppModalService.showModal('Export', 'Export the current results?', function() {
			// determine export file type
			var response = fxAppModalService.getModalOptions().response;
			if (response) {
				// generate the file
				var file = csrViewService.exportSearchResults(fxAppTreeService.treeData, response);
				var filename = 'export_' + moment().format('YYYY-MM-DD_HH-mm-ss') + '.' + response.toLowerCase();
				// download the file
				csrViewService.downloadString(file, filename);
			}
		}, {
			showCancelButton: true,
			customButtons: ['CSV', 'HTML'],
			response: ''
		});
	};

	$.AdminLTE.layout.fix();
}]);
