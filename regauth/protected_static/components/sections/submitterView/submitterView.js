/**
 * The base HTML of the submitter view
 */
fxApp.component('submitterView', {
	templateUrl: 'components/sections/submitterView/content.html'
});

/**
 * Submitter form controller
 */
var submitterFormCtrl = ['$scope', 'submitterViewService', '$timeout', 'fxAppService', function($scope, submitterViewService, $timeout, fxAppService) {
	$scope.submitterViewService = submitterViewService;
	$scope.fxAppService = fxAppService;
	$scope.ctrl = this;

	// form steps
	$scope.progressBarPx = 400;
    $scope.stepHolder = submitterViewService.getFormSteps($scope);
    $scope.getStepList = function() {
        var stepList = function () {
            var ret = [];

            // Select the certificate that will sign the request
            ret.push('signingCert');

            // Select the approval group
            ret.push('approvalGroup');

            // Force user to authenticate via LDAP before continuing
            if ($scope.ctrl.formdata.issuancePolicyData.ldapAuth) {
                ret.push('ldapAuth')
            }

            if ($scope.isHash) {
                // Upload file hash to sign
                ret.push('uploadHash');
            } else if ($scope.ctrl.tokendata.is_local_token) {
                // Select X.509 v3 Extensions
                ret.push('v3Profile');
                // Create a custom subject X.509 name
                ret.push('dn');
            } else if (!$scope.ctrl.formdata.isGeneratedPKI) {
                // Allow the user to upload a CSR
                ret.push('uploadCsr');
                // Select X.509 v3 Extensions
                ret.push('v3Profile');
                // Create a custom subject X.509 name
                ret.push('dn');
            } else {
                // Select X.509 v3 Extensions
                ret.push('v3Profile');
                // Create a custom subject X.509 name
                ret.push('dn');
            }

            ret.push('config');

            return ret;
        }

        return stepList().map(function(step) {
            return $scope.stepHolder[step];
        });
    };

    $scope.steps = $scope.getStepList();
	$scope.currentStep = $scope.steps[0];

	$scope.selectStep = function(name) {
		$scope.steps.map(function(step) {
			if (name === step.name) {
				$scope.currentStep = step;
			}
		});
	};

	$scope.prevStep = function() {
		var index = $scope.getCurrentStepIndex();
		if (index > 0) {
			$scope.currentStep = $scope.steps[index-1];
		}
	};

	$scope.nextStep = function() {
		var index = $scope.getCurrentStepIndex();
        var changePage = function () {
            $scope.currentStep = $scope.steps[index+1];
        };

		if (index < $scope.steps.length-1) {
            $scope.currentStep.finish(changePage);
		}
	};

	$scope.getCurrentStepIndex = function() {
		var result = 0;
		$scope.steps.map(function(step, index) {
			if ($scope.currentStep.name === step.name) {
				result = index;
			}
		});
		return result;
	};

	$scope.getProgressWidth = function() {
		var unitOfWidth = Math.floor($scope.progressBarPx / $scope.steps.length);
		var index = $scope.getCurrentStepIndex();
		return (unitOfWidth * index + Math.floor(unitOfWidth / 2)).toString() + 'px';
	};

	$scope.cssPx = function(numPixels) {
		return numPixels + 'px';
	};

	$scope.stepDotColor = function(index) {
		var lightGray = '#ccc';
		var gray = '#aaa';
		var red = '#911111';

		var currentIndex = $scope.getCurrentStepIndex();

		// Completed steps
		if (index < currentIndex) {
			return gray;
		}
		// Current step
		else if (index === currentIndex) {
			return red;
		}
		// Steps remaining
		else {
			return lightGray;
		}
	};

	$scope.stepDotSize = function(index) {
		return index === $scope.getCurrentStepIndex() ? '15px' : '12px';
	};

	$scope.stepDotShadow = function(index) {
		return index === $scope.getCurrentStepIndex() ? '#777 2px 2px 5px' : 'none';
	};

	/**
	 * Check the progress of the current step when it is selected
	 */
	$scope.$watch('currentStep', function() {
		$scope.currentStep.validate();
	});


    $scope.setObjectType = function() {
        if ($scope.isHash === true) {
            $scope.ctrl.formdata.objectType = 'SIGNABLE_OBJ';
        } else {
            $scope.ctrl.formdata.objectType = 'CERT_REQ';
        }
    }

	/**
	 * Check the progress of the current step when form data changes
	 */
	$scope.$watch('ctrl.formdata', function() {
		$scope.currentStep.validate();
	}, true);

    $scope.$watch('ctrl.requestsource', function() {
        var genSource = $scope.ctrl.requestsource;
        $scope.ctrl.formdata.isGeneratedPKI = false;
        $scope.ctrl.tokendata.is_local_token = false;
        $scope.isHash = false;
        if (genSource === 'local') {
			$scope.ctrl.tokendata.is_local_token = true;
			$scope.showSmartTokenGenerationHint();
        } else if (genSource === 'remote') {
			$scope.ctrl.formdata.isGeneratedPKI = true;
        } else if (submitterViewService.isBrowserHash(genSource)) {
            $scope.ctrl.uploadLabel = "Hash a file";
            $scope.isHash = true;
        } else if (submitterViewService.isHashUpload(genSource)) {
            $scope.ctrl.uploadLabel = "Upload a file hash";
            $scope.isHash = true;
        } else {
            $scope.ctrl.uploadLabel = "Upload a request";
        }

        $scope.steps = $scope.getStepList();
        $scope.setObjectType();
	});

    /**
     * Updates the steps when the issuance policy changes
     */
    $scope.$watch('ctrl.formdata.issuancePolicyData', function() {
        $scope.steps = $scope.getStepList();
    });

	/**
	 * Called when the key type is changed for a generated PKI request
	 */
	$scope.$watch('ctrl.formdata.keyTypeSelected', function() {
		if ($scope.ctrl.formdata.isGeneratedPKI && $scope.ctrl.formdata.keyTypeSelected) {
			var keyTypeSelected = submitterViewService.getObjKeys($scope.ctrl.formdata.keyTypeSelected)[0];

			$scope.ctrl.formdata.keyTypeSelectedSize = submitterViewService.determineInitialKeyTypeValue(
				submitterViewService.getFirstInnerValue($scope.ctrl.formdata.keyTypeSelected),
				submitterViewService.keyTypeDefs().defaultSizes[keyTypeSelected]
			);
		}
	});

	/**
	 * Displays a hint about how long the CSR generation process might take.
	 */
	$scope.showSmartTokenGenerationHint = function() {
		if ($scope.ctrl.tokendata.is_local_token) {
			$('#continue-arrow').notify(
				'Continuing will generate your CSR.\nThis may take up to a minute.',
				{ position: 'left middle',
				  autoHide: true,
				  autoHideDelay: 10000,
				  className: 'info' }
			);
		}
	};

	/**
	 * Displays a hint if no CSR is uploaded yet
	 */
	$scope.showUploadHint = function() {
		if (!$scope.ctrl.formdata.request.length) {
            var uploadType = $scope.isHash ? 'File' : 'CSR';
			$('input#raw-file').notify(
                'Click to upload a ' + uploadType,
				{ position: 'top left' }
			);
		}
	};

	/**
	 * Sets up the upload hint callback and is called as soon as the
	 * button it points to exists in the DOM
	 */
	$scope.setUploadHint = function() {
		$('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
			if (e.target.href.split('#')[1] === 'upload') {
				$scope.showUploadHint();
			}
		});
	};

	/**
	 * Called every time the extension data is changed by the user
	 */
	$scope.$watch('ctrl.formdata.v3Extensions', function() {
		if ($scope.ctrl.formdata.v3Extensions) {
			submitterViewService.updateExtensionValues($scope.ctrl.formdata.v3Extensions);
		}
	}, true);

	/**
	 * Called every time the extension options change
	 */
	$scope.$watch('ctrl.formdata.v3ExtOptions', function() {
		// Sort the options
		if ($scope.ctrl.formdata.v3ExtOptions) {
			$scope.ctrl.selectedExtension = submitterViewService.sortExtOptions($scope.ctrl.formdata.v3ExtOptions);
			$scope.ctrl.formdata.v3ExtOptions = submitterViewService.removeDuplicateOptions(
				$scope.ctrl.formdata.v3ExtOptions,
				$scope.ctrl.formdata.v3Extensions
			);
		}
	}, true);
}];

/**
 * Submitter form
 */
fxApp.component('submitterForm', {
	templateUrl: 'components/sections/submitterView/submitterForm.html',
	bindings: {
		formdata:             '=',
		approvalgroups:       '=',
		issuancepolicies:     '=',
		signingcerts:         '=',
		selectapprovalgroup:  '=',
		selectsigningcert:    '=',
        fileupload:           '=',
		csrupload:            '=',
		submit:               '=',
		tokendata:            '=',
		fxcng:                '=',
        requestsource:        '='
	},
	controller: submitterFormCtrl
});

/**
 * The submitter view controller
 */
var submitterViewCtrl = fxApp.controller('submitterViewCtrl',
	['$scope', '$rootScope', '$http', '$q', 'fxAppService', 'submitterViewService', 'fxAppModalService',
	function($scope, $rootScope, $http, $q, fxAppService, submitterViewService, fxAppModalService) {

	$scope.fxAppService = fxAppService;
	$scope.submitterViewService = submitterViewService;

	$scope.fxcng = $scope.fxAppService.getFXCNGPlugin();

	if ($scope.fxcng) {
		$scope.list_token_providers = $scope.fxcng.getProviders();
	}

	// FORMS
	$scope.fxForms = this;
	$scope.fxForms.submitterForm = {
		approvalGroups: [],
        shownApprovalGroups: [],
		issuancePolicies: [],
		signingCerts: [],
        requestsource: "neither",
		tokendata: {
			is_local_token: false,
			list_providers: $scope.list_token_providers,
		},
		data: {
			"aliases": "",
			"childType": "UNKNOWN",
			"expiration": "",
			"extensionProfile": "",
			"hash": "",
			"hashAlgorithm": "",
			"isSavePkiKey": false,
			"keyStorage": "protected",
			"keyType": "",
			"loadTime": submitterViewService.ISOTimetoFXTime(new Date().toISOString()),
			"isGeneratedPKI": false,
            "ldapAuth": false,
            "ldapUsername": "",
            "ldapPassword": "",
			"name": "",
			"notes": "",
			"emails": "",
			"numChildren": 0,
            "objectID": "-1",
			"objectType": "",
			"ownerID": "0",
			"parentID": "",
			"parentType": "APPROVAL_GROUP",
			"path": "",
            "password": "",
            "verify_password": "",
            "fileRequest": "",
            "textRequest": "",
			"request": "",
            'saltLength': '0',
            'padding': '',
			"signedCert": "",
			"signingApprovals": [],
			"signingCert": "",
			"status": "Pending",
			"subject": {},
			"parseCSR": false,
			"uploaderId": fxAppService.getLoginData().primaryIdentity.id,
			"uploaderName": fxAppService.getLoginData().primaryIdentity.name,
			"approvalGroupData": {},
			"issuancePolicyData": {},
			"signingCertData": {},
			"uniqueID": "",
			"policyID": "",
			"token_provider_name": "Microsoft Smart Card Key Storage Provider",
			"token_key_name": "Name your key pair"
		},

        ldapPasswordCallback: function (password) {
            $scope.fxForms.submitterForm.data.ldapPassword = password;
        },

        ldapUsernameCallback: function (username) {
            $scope.fxForms.submitterForm.data.ldapUsername = username;
        },

        /**
         * Called on file load of csr to fill out CSR box
         *
         * @param {File}  file  Signing request file
         * @returns {promise}  Promise containing the display text
         */
        fileUploadCallback: function (file) {
            $scope.fxForms.submitterForm.data.request = '';
            if ($scope.fxForms.submitterForm.requestsource === 'localHash') {
                $scope.fxForms.submitterForm.data.name = file.name;
                return submitterViewService.slowPromise(function () {
                    return submitterViewService.handleFileHash($scope.fxForms.submitterForm.data, file);
                });
            } else if ($scope.fxForms.submitterForm.requestsource === 'uploadHash') {
                return submitterViewService.readHashFromFile($scope.fxForms.submitterForm.data, file);
            } else {
                return submitterViewService.handleRequestFile($scope.fxForms.submitterForm.data, file);
            }
        },

		/**
		 * Called when a request is uploaded to parse it server-side
		 *
		 * @param {string}    filestring - hex-encoded file
		 */
		csrUploadCallback: function(filestring) {
            return submitterViewService.setFormFromCSR($scope.fxForms.submitterForm.data, filestring);
		},

		/**
		 * Called when "Submit" button is clicked
		 */
		submitCallback: function() {
			// Convert data into the format expected by the server side
			submitterViewService.prepareCsr($scope.fxForms.submitterForm.data).then(function(csr) {
				// Default modal info
				var modalInfo = {
					title: 'Validation Failed',
					message: ''
				};

				// Client-side validation
				submitterViewService.clientValidateCsr(csr).then(function() {
					// Client-side validation passed
					return $q.resolve();
				}, function(message) {
					// Client-side validation failed
					modalInfo.message = message;
					return $q.reject();
				}).then(function() {
					var deferred = $q.defer();

					// Server-side validation
					submitterViewService.validateCsr(csr).then(function(data) {
						submitterViewService.submitCsr(csr);
					}, function(data) {
						modalInfo.message = data.objectData.message;
						deferred.reject();
					});

					return deferred.promise;
				}).finally(function() {
					fxAppModalService.showModal(modalInfo.title, modalInfo.message);
				});
			});
		},

		/**
		 * Called when an approval group is selected from the dropdown menu
		 *
		 * @param {string}    approvalGroup - the selected approval group
		 */
		selectApprovalGroupCallback: function() {
			return function(approvalGroup) {
				$scope.fxForms.submitterForm.data = submitterViewService.selectApprovalGroup(
					approvalGroup,
					$scope.fxForms.submitterForm.data
				);
			};
		},

		/**
		 * Called when an signing cert is selected from the dropdown menu
		 *
		 * @param {string}    signingCert - the selected signing cert
		 */
		selectSigningCertCallback: function(signingCert) {
			$scope.fxForms.submitterForm.data = submitterViewService.selectSigningCert(
				signingCert,
				$scope.fxForms.submitterForm.data
			);

			$scope.fxForms.submitterForm.data = submitterViewService.selectIssuancePolicy(
				signingCert.policyID,
				$scope.fxForms.submitterForm.issuancePolicies,
				$scope.fxForms.submitterForm.data
			);

            $scope.fxForms.submitterForm.shownApprovalGroups = submitterViewService.updateIssuanceApprovalGroup(
                $scope.fxForms.submitterForm.approvalGroups,
                $scope.fxForms.submitterForm.data
            );

            submitterViewService.selectApprovalGroup(
                $scope.fxForms.submitterForm.shownApprovalGroups[0],
                $scope.fxForms.submitterForm.data
            );
		}
	};

	// called when the extension profile is selected
	$scope.$watch('fxForms.submitterForm.data.extensionProfile', function() {
		if ($scope.fxForms.submitterForm.data.signingCertData) {
			submitterViewService.getProfileExtensionSet(
				$scope.fxForms.submitterForm.data.extensionProfile,
				$scope.fxForms.submitterForm.data.signingCertData.objectID
			).then(function(data) {
				$scope.fxForms.submitterForm.data.v3Extensions = data.extensions;
				$scope.fxForms.submitterForm.data.extensionProfileData = data.profile;
			});
		}
	});

	// get the approval groups while the page loads
	submitterViewService.getApprovalGroups().then(function(data) {
		if (data.length) {
			$scope.fxForms.submitterForm.approvalGroups = data;
            $scope.fxForms.submitterForm.shownApprovalGroups = data;

			$scope.fxForms.submitterForm.data = submitterViewService.selectApprovalGroup(
				data[0],
				$scope.fxForms.submitterForm.data
			);
		}
	});

	// get the signing certs while the page loads
	submitterViewService.getSigningCerts().then(function(certData) {
		if (certData.length) {
			// get the issuance policies
			submitterViewService.getIssuancePolicies('X509CERT', certData.map(function(cert){
				return cert.objectID;
			})).then(function(policyData) {
				if (policyData.length) {
					$scope.fxForms.submitterForm.issuancePolicies = policyData;

					// set the signing cert data
					$scope.fxForms.submitterForm.signingCerts = certData.reduce(function(result, cert){
						// find the policy associated with the signing cert
						var policies = policyData.filter(function(policy) {
							return policy.objectID === cert.policyID;
						});
						if (policies.length != 1) {
							console.error('Failed to find issuance policy for signing certificate "%s" matching %d', cert.name, cert.policyID);
							return result;
						}

						var policy = policies[0];

						// Certs should know if their policies allow generated PKI, and uploaded CSRs.
						cert.allowPKIGen = policy.allowPKIGen;
                        cert.allowUploads = policy.allowUploads;
                        cert.allowHash = policy.allowObjectSigning;
                        cert.policyName = policy.displayName;

						result.push(cert);
						return result;
					}, []);

                    $scope.fxForms.submitterForm.selectSigningCertCallback(certData[0]);

					// set additional form data
					$scope.fxForms.submitterForm.data.v3ExtOptions = submitterViewService.getAllExtensions();
				}
				else {

				}
			});
		}
	});

	// Get the DN profiles while the page loads
	submitterViewService.getDNProfilesAsFormData(['Classic']).then(function(profiles) {
		// Initialize the DN form
		$scope.fxForms.submitterForm.data.DNProfiles = profiles;
		$scope.fxForms.submitterForm.data.selectedDNProfile = profiles[0];
		$scope.fxForms.submitterForm.data.subject = profiles[0].extensions;
	});

	$.AdminLTE.layout.fix();
}]);
