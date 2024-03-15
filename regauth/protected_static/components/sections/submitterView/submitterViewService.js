/**
 * Provides commonly used functions for the submitter view
 *
 * @returns {object}    helper functions injected into the submitter view controller
 */

var submitterViewService = fxApp.factory('submitterViewService',
    ['$http', '$q', '$timeout', 'fxAppService', 'fxAppViewService', 'fxAppModalService', 'fxIOService', 'fxEncodeService',
    function($http, $q, $timeout, fxAppService, fxAppViewService, fxAppModalService, fxIOService, fxEncodeService) {

		var fxcng = fxAppService.getFXCNGPlugin();

		/**
		 * Converts a CERT_REQ back into its original format
		 *
		 * @param   {object}    csr - the certificate signing request
		 * @returns {object}    a CERT_REQ in its original format
		 */
		function prepareCsr(csr) {
			var deferred = $q.defer();

			deferred.resolve((function() {
				// Copy the form data
				var preparedCsr = JSON.parse(JSON.stringify(csr));

				// Set the DN
				preparedCsr.subject = fxAppViewService.subjectToString(
					fxAppViewService.maskDNWithProfile(preparedCsr)
				);

				// Set other fields
				preparedCsr.emails = fxAppViewService.strToCSV(csr.emails);
				preparedCsr.policyID = csr.signingCertData.policyID;

				// Set the key type if using generated PKI
				if (csr.isGeneratedPKI){
					preparedCsr.keyType = fxAppViewService.keyTypeToString(
						fxAppViewService.getObjKeys(csr.keyTypeSelected)[0],
						csr.keyTypeSelectedSize
					);
                    preparedCsr.password = fxAppViewService.hexEncode(csr.password);
                    preparedCsr.verify_password = fxAppViewService.hexEncode(csr.verify_password);
				}

				// set the extensions
				preparedCsr.v3ExtensionDesc = fxAppViewService.createExtensionDescriptions(preparedCsr.v3Extensions);
				preparedCsr.v3Extensions = fxAppViewService.createV3ExtensionsString(preparedCsr.v3Extensions);

				return preparedCsr;
			})());

			return deferred.promise;
		}

        /**
         * Picks the request and prepares the data
         *
         * @param {string}  textRequest The displayed request value (preferred)
         * @param {string}  fileRequest The request from an uploaded file
         * @returns {string}  choice The chosen request
         */
        function pickRequest(textRequest, fileRequest) {
            var choice = '';
            if (fxAppViewService.isPEM(textRequest)) {
                choice = fxAppViewService.hexEncode(textRequest);
            } else if (textRequest) {
                choice = textRequest;
            } else if (fileRequest) {
                choice = fileRequest;
            }

            return choice;
        }

		/**
		 * Submit a CERT_REQ
		 *
		 * @param   {object}    csr - the certificate signing request
		 */
		function submitCsr(csr) {
			var csrSubmitQuery = {
				"method": "create",
                "objectData": {}
			};

            csrSubmitQuery.objectData[csr.objectType] = [csr];

			// Only reload the window once the POST is complete.
			$http.post(window.apipath('/object'), csrSubmitQuery).then( function(result) { 
				window.location.reload(); 
			});
		}

		/**
		 * Populates the submitter form with data from the selected REG_AUTH
		 *
		 * @param   {string}    policyID - the selected signing cert's policy ID
		 * @param   {array}     issuancePolicies - the available issuance policies
		 * @param   {object}    formdata - the data the form expects
		 * @returns {object}    the updated form data
		 */
		function selectIssuancePolicy(policyID, issuancePolicies, formdata) {
			// find the associated policy
			var issuancePolicy = {};
			for(var i=0; i<issuancePolicies.length; i++) {
				if (issuancePolicies[i].objectID === policyID) {
					issuancePolicy = issuancePolicies[i];
					break;
				}
			}

			// set the form data
			formdata.issuancePolicyData = issuancePolicy;
			formdata.expiration = issuancePolicy.expiration;
            
            if (typeof(issuancePolicy.hashAlgorithms) === "string") {
                issuancePolicy.hashAlgorithms = issuancePolicy.hashAlgorithms.split(',');
            }
			
            formdata.hashAlgorithm = issuancePolicy.hashAlgorithms[0];
			formdata.extensionProfile = Object.keys(issuancePolicy.profiles)[0];
			formdata.keyTypeSelected = fxAppViewService.getFirstInnerObj(issuancePolicy.keyTypes);

            // Hash specific options
            if (typeof(issuancePolicy.paddingModes) === "string") {
                issuancePolicy.paddingModes = issuancePolicy.paddingModes.split(',');
            }

            formdata.padding = issuancePolicy.paddingModes[0];
            formdata.saltLength = 0;

			var keyTypeSelected = fxAppViewService.getObjKeys(formdata.keyTypeSelected)[0];
			formdata.keyTypeSelectedSize = fxAppViewService.determineInitialKeyTypeValue(
				fxAppViewService.getFirstInnerValue(formdata.keyTypeSelected),
				fxAppViewService.keyTypeDefs().defaultSizes[keyTypeSelected]
			);

			return formdata;
		}

		/**
		 * Populates the submitter form with data from the selected APPROVAL_GROUP
		 *
		 * @param   {object}    approvalGroup  - the selected approval group
		 * @param   {object}    formdata - the data the form expects
		 * @returns {object}    the updated form data
		 */
		function selectApprovalGroup(approvalGroup, formdata) {
			formdata.approvalGroupData = approvalGroup;
			formdata.parentID = approvalGroup.objectID;

			return formdata;
		}

		/**
		 * Populates the submitter form with data from the selected X509CERT
		 *
		 * @param   {object}    signingCert  - the selected approval group
		 * @param   {object}    formdata - the data the form expects
		 * @returns {object}    the updated form data
		 */
		function selectSigningCert(signingCert, formdata) {
			formdata.signingCertData = signingCert;
			formdata.signingCert = signingCert.objectID;

			return formdata;
		}

        /**
         * Creates the approval group step
         * @param {object}  scope  The submitter form scope
         * @returns {object}  The approval group step
         */
        function approvalGroupStep(scope) {
            return fxAppViewService.createStep('approvalGroup', 'Approval Group', function validate() {
                this.canContinue = scope.ctrl.formdata.approvalGroupData.objectID ? true : false;
            });
        }

        /**
         * Update the approval group list with the selected issuance policy
         * @param {array}  approvalGroupList  The list of viewable approval groups
         * @param {object}  formData  The form information
         * @returns {object}  shownApprovalGroups  The list of shown approval groups
         */
        function updateIssuanceApprovalGroup(approvalGroupList, formData) {
            var issuancePolicy = formData.issuancePolicyData;
            var shownApprovalGroups = [];
            if (issuancePolicy && issuancePolicy.approvalGroupId && issuancePolicy.approvalGroupName) {
                // Add the default approval group
                shownApprovalGroups.push({
                    objectID: issuancePolicy.approvalGroupId,
                    name: issuancePolicy.approvalGroupName
                })

                // Remove any groups that already exist in our list
                shownApprovalGroups = shownApprovalGroups.filter(function (group) {
                    for (var i in approvalGroupList) {
                        if (approvalGroupList[i].objectID === group.objectID) {
                            return false;
                        }
                    }

                    return true;
                });
            }

            // Append the remaining approval groups
            if (shownApprovalGroups.length > 0) {
                shownApprovalGroups = shownApprovalGroups.concat(approvalGroupList);
            } else {
                shownApprovalGroups = approvalGroupList;
            }

            return shownApprovalGroups;
        }

        /**
         * Creates the signing cert selection step
         * @param {object}  scope  The submitter form scope
         * @returns {object}  The signing cert step group step
         */
        function signingCertStep(scope) {
            return fxAppViewService.createStep('signingCert', 'Signing Certificate', function validate() {
                var hasSigningCert = scope.ctrl.formdata.signingCertData.objectID ? true : false;
                var hasIssuancePolicy = scope.ctrl.formdata.issuancePolicyData.objectID ? true : false;

                // Ensure that at least a cert was selected
                if (hasSigningCert && hasIssuancePolicy) {
                    var bCanUpload = scope.ctrl.formdata.issuancePolicyData.allowUploads;
                    var bCanHash = scope.ctrl.formdata.issuancePolicyData.allowObjectSigning;
                    var allowPKIGen = scope.ctrl.formdata.signingCertData.allowPKIGen;
                    
                    var bIsHash = scope.isHash;
                    var isGeneratedPKI = scope.ctrl.formdata.isGeneratedPKI;
                    var bLocalToken = scope.ctrl.tokendata.is_local_token;

                    if (!bCanUpload && !isGeneratedPKI && !bLocalToken && !bIsHash) {
                        this.canContinue = false;
                    } else if (isGeneratedPKI) {
                        this.canContinue = allowPKIGen;
                    } else if (bIsHash) {
                        this.canContinue = bCanHash;
                    } else if (bLocalToken) {
                        this.canContinue = scope.ctrl.formdata.token_provider_name &&
                            scope.ctrl.formdata.token_key_name &&
                            scope.ctrl.formdata.keyTypeSelectedSize;
                    }
                    else {
                        this.canContinue = true;
                    }
                }
            }, function finish(updateCallback) {
                
                var tokendata = scope.ctrl.tokendata;
                if (tokendata.is_local_token !== true || !scope.fxAppService.isInternetExplorer()) { 
                    updateCallback();
                }
                
                var formdata = scope.ctrl.formdata;
                var checkAndFinish = function() {
                    if (formdata.request !== '') {
                        updateCallback();
                    }
                };

                /**
                 * Does the actual CSR request
                 * @param {string}  request  The CSR request to send to the server
                 */
                var doRequest = function(request) {
                    if (!request) {
                        return;
                    }

                    var serverRequest = function() {
                        return setFormFromCSR(formdata, request);
                    };

                    fxAppViewService.slowPromise(serverRequest).then(checkAndFinish);
                };

                // The first block handles the IE token generation
                var limitedGenerate = function () {
                    var generate = function () {
                        return generateCSR(formdata, doRequest);
                    };

                    var maximumTime = 500;
                    return $timeout(generate, maximumTime);
                };

                fxAppViewService.slowPromise(limitedGenerate);
            });
        }

        function ldapAuthStep(scope) {
            return fxAppViewService.createStep('ldapAuth', "LDAP Authenticate", function validate() {
                if (scope.ctrl.formdata.ldapUsername && scope.ctrl.formdata.ldapPassword) {
                    this.canContinue = true;
                } else {
                    this.canContinue = false;
                }
            }, function finish(updateCallback) {
                var formdata = scope.ctrl.formdata;
                var checkAndFinish = function() {
                    if (formdata.ldap_auth.authenticated) {
                        updateCallback();
                    }
                }

                var setFormFromLDAPAuth = function(policyID, ldapUsername, ldapPassword) {

                    function setFormFromData(data) {

                        formdata.ldap_auth = data.formData.ldap_auth
                    };

                    return fxAppViewService.ldapAuth(policyID, ldapUsername, ldapPassword).then(setFormFromData);
                }

                var performLDAPAuth = function() {
                    var policyID = formdata.issuancePolicyData.objectID;
                    var ldapUsername = formdata.ldapUsername;
                    var ldapPassword = formdata.ldapPassword;
                    return setFormFromLDAPAuth(policyID, ldapUsername, ldapPassword);
                }

                fxAppViewService.slowPromise(performLDAPAuth).then(checkAndFinish)
            });
        }

        /**
         * Creates the CSR upload step
         * @param {object}  scope  The submitter form scope
         * @returns {object}  The CSR upload step
         */
        function uploadCsrStep(scope) {
            return fxAppViewService.createStep('uploadCsr', 'Upload Request', function validate() {
                if (scope.ctrl.formdata.textRequest || scope.ctrl.formdata.fileRequest) {
                    this.canContinue = true;
                } else {
                    this.canContinue = false;
                }
            }, function finish(updateCallback) {
                var formdata = scope.ctrl.formdata;
                var checkAndFinish = function() {
                    if (formdata.request !== '') {
                        updateCallback();
                    }
                };

                /**
                 * Does the actual CSR request
                 * @param {string}  request  The CSR request to send to the server
                 */
                var doRequest = function(request) {
                    if (!request) {
                        return;
                    }

                    var serverRequest = function() {
                        return setFormFromCSR(formdata, request);
                    };

                    fxAppViewService.slowPromise(serverRequest).then(checkAndFinish);
                };

                var tokendata = scope.ctrl.tokendata;
                if (tokendata.is_local_token !== true) {
                    // All other csr types go here
                    var textRequest = formdata.textRequest;
                    var fileRequest = formdata.fileRequest;
                    var request = pickRequest(textRequest, fileRequest);
                    doRequest(request);
                }
            });
        }

        /**
         * Creates the hash upload step
         * @param {object}  scope  The submitter form scope
         * @returns {object}  The hash upload step
         */
        function uploadHashStep(scope) {
            return fxAppViewService.createStep('uploadHash', 'Upload Request', function validate() {
                var formdata = scope.ctrl.formdata;
                var checkBitLength = function() {
                    var hashBitLengths = {
                        MD5: 128,
                        RIPEMD: 160,
                        SHA1: 160,
                        SHA224: 224,
                        SHA256: 256,
                        SHA384: 384,
                        SHA512: 512
                    };

                    var bitLength = fxEncodeService.hexToBitLength(formdata.hash);
                    return hashBitLengths[formdata.hashAlgorithm] === bitLength;
                };

                var checkPadding = function() {
                    return formdata.padding !== 'PSS' ||
                        Number(formdata.saltLength).toFixed() === formdata.saltLength.toString();
                };

                var checkHex = function () {
                    return /^[A-Fa-f0-9]+$/.test(formdata.hash);
                }

                formdata.hash = formdata.hash.trim();
                this.canContinue = checkBitLength() && checkPadding() && checkHex();
            });
        }

        /**
         * Creates the X509v3 extension step
         * @param {object}  scope  The submitter form scope
         * @returns {object}  The X509v3 extension step
         */
        function v3ProfileStep(scope) {
            return fxAppViewService.createStep('v3Profile', 'Extension Profile', function validate() {
                this.canContinue = scope.ctrl.formdata.extensionProfile ? true : false;
            });
        }


        /**
         * Creates the distinguished name step
         * @param {object}  scope  The submitter form scope
         * @returns {object}  The distinguished name step
         */
        function distinguishedNameStep(scope) {
            return fxAppViewService.createStep('dn', 'Distinguished Name', function() {
                // The schema for the currently selected DN profile
                var extensions = scope.ctrl.formdata.selectedDNProfile.extensions;

                // If the DN profile has these extensions,
                // the user must fill in a value before continuing
                var requiredExtensions = [
                    { name: 'commonName', oid: 'OID_2_5_4_3', exists: false, hasValue: false }
                ];

                // Find required extensions in the profile schema
                Object.keys(extensions).map(function(extensionOID) {
                    requiredExtensions.map(function(requiredExtension) {
                        // Check by OID
                        if (extensionOID === requiredExtension.oid) {
                            // This profile has this extension
                            requiredExtension.exists = true;

                            // Get the "subject" (where the form gets the value from)
                            var extension = scope.ctrl.formdata.subject[requiredExtension.oid];

                            // Check that the form has the OID and that
                            // the value is a non-empty string
                            requiredExtension.hasValue = extension !== undefined &&
                                typeof extension.value === 'string' &&
                                !(extension.value.length < 1);
                        }
                    });
                });

                // Determine whether the user can continue by finding the extensions
                // that failed the previous check
                this.canContinue = requiredExtensions.filter(function(requiredExtension) {
                    return requiredExtension.exists && !requiredExtension.hasValue;
                }).length < 1;
            });
        }

        /**
         * Creates the configuration step
         * @param {object}  scope  The submitter form scope
         * @returns {object}  The configuration step
         */
        function configStep(scope) {
            return fxAppViewService.createStep('config', 'Configure Request', function() {
                var hasName = scope.ctrl.formdata.name ? true : false;
                var hasHashAlgorithm = scope.ctrl.formdata.hashAlgorithm ? true : false;
                var hasExpiration = scope.ctrl.formdata.expiration ? true : false;

                if (hasName && hasHashAlgorithm && hasExpiration) {
                    var isGeneratedPKI = scope.ctrl.formdata.isGeneratedPKI;

                    if (isGeneratedPKI) {
                        var hasEmails = scope.ctrl.formdata.emails ? true : false;
                        var hasKeyTypeSelected = scope.ctrl.formdata.keyTypeSelected ? true : false;
                        var hasKeyTypeSelectedSize = scope.ctrl.formdata.keyTypeSelectedSize ? true : false;
                        var hasPassword = scope.ctrl.formdata.password ? true : false;
                        var hasVerifyPassword = scope.ctrl.formdata.verify_password ? true : false;

                        this.canContinue = hasEmails && hasKeyTypeSelected &&
                            hasKeyTypeSelectedSize && hasPassword && hasVerifyPassword;
                    }
                    else {
                        this.canContinue = true;
                    }
                }
            });
        }

		/**
		 * Returns the JSON that defines all the steps of the submitter form
		 *
		 * @param   {object}    scope - submitter form controller scope
		 * @returns {object}    submitter form steps
		 */
		function getFormSteps(scope) {
            return {
                approvalGroup: approvalGroupStep(scope),
                config: configStep(scope),
                dn: distinguishedNameStep(scope),
                signingCert: signingCertStep(scope),
                ldapAuth: ldapAuthStep(scope),
                uploadCsr: uploadCsrStep(scope),
                uploadHash: uploadHashStep(scope),
                v3Profile: v3ProfileStep(scope)
            };
        }

		/**
		 * Uses the FxCNG plugin to generate a CSR on a smart token.
		 *
		 * @param   {object}    objFormData - Form data from the page.
         * @param   {function}  generateCallback - Function called on successful generation
         *
		 * @returns {string}    CSR generated, or null/empty string on error.
		 */
		function generateCSR(objFormData, generateCallback) {

			if (!fxcng) {
                return null;
			}

            var postGenerate = function (csr) {
                if (!csr) {
                    var err = "The smart token failed to generate a certificate signing request.";
                    fxAppModalService.showModal(err, 'CSR Generation Failed');
                } else {
                    generateCallback(csr);
                }
            };

			return postGenerate(fxcng.generateCSR(objFormData.token_provider_name,
                                     objFormData.token_key_name,
				                     fxAppViewService.getObjKeys(objFormData.keyTypeSelected)[0],
                                     objFormData.keyTypeSelectedSize));
		}

        /**
         * Handle a CSR request file
         * @param {object}  formData  The data object for the form
         * @return {promise}  promise  A promise containing the display string
         *
         */
        function handleRequestFile(formData, file) {
           /**
             * Sets the various request values
             * @param {string}  fileRequest  Hex encoded file string
             * @param {string}  textRequest  Clear file ( if file is not binary/DER )
             * @returns {string}  The textRequest if it exists if not the file request
             */
            function assignRequest(fileRequest, textRequest) {
                formData.fileRequest = fileRequest;
                formData.textRequest = textRequest;
                return textRequest ? textRequest : fileRequest;
            };

            return fxIOService.readSigningRequest(file).then(function(filestring) {
                var text = '';
                if (fxAppViewService.isPEM(filestring, true)) {
                    text = fxEncodeService.hexDecode(filestring);
                }

                return assignRequest(filestring, text);
            }, function() {
                return assignRequest('', '');
            });
        }

        /**
         * Hashes a file
         * @param {object}  formData  the form to set
         * @param {File}  file  the file to hash
         * @return {promise} Promise containing the file hash
         */
        function handleFileHash(formData, file) {
            return fxIOService.hashFile(formData.hashAlgorithm, file).then(function(digest) {
                formData.textRequest = digest;
                formData.hash = digest;
                return digest;
            });
        }

        /**
         * Set form data using a csr file string
         * @param {object}  formdata  The object to fillout
         * @param {string}  filestring  The string value of the csr
         * @returns {promise}  The promise from setting the form data
         */
        function setFormFromCSR(formdata, filestring) {
            function setFormFromData(data) {
                // Check if the file was parsed
                if(!data.hash) {
                    fxAppModalService.showModal("CSR Upload", "Please upload a valid certificate signing request");
                }
                else {
                    // Set the form data
                    formdata.subject = data.subject ? fxAppViewService.subjectParse(data.subject) : "";
                    formdata.hash = data.hash ? data.hash : "";
                    formdata.keyType = data.keyType ? data.keyType : "";
                    formdata.request = data.request ? data.request : "";
                }
            }

            return fxAppViewService.getFormDataFromUploadedCsr(filestring).then(setFormFromData);
        }

        /**
         * Read a hash file for a single hash
         * @param {object}  formdata  Object to assign the file name to
         * @param {File}  file  The file to read the hash from
         */
        function readHashFromFile(formdata, file) {
            function textRead(reader, file) {
                reader.readAsText(file);
            }

            // sha1sum/md5deep format: {HASH}{WHITESPACE}{FILENAME}
            return fxIOService.readFile(textRead, file).then(function(filedata) {
                // Currently we only support one hash per file
                var hashinfo = filedata.split(/\s+/);
                formdata.name = hashinfo[1];
                formdata.textRequest = hashinfo[0];
                return hashinfo[0];
            });
        }

        /**
         * Check if this request is an in-browser hash or not
         * @param {string}  requestSource  The generation type
         * @returns  {boolean}  True if in-browser hash false otherwise
         */
        function isBrowserHash(requestSource) {
            return requestSource === 'localHash';
        }

        /**
         * Check if this request is a hash uploaded from a file
         * @param {string}  requestSource  The generation type
         * @returns  {boolean}  True if uploaded hash false otherwise
         */
        function isHashUpload(requestSource) {
            return requestSource === 'uploadHash';
        }

        /**
         * Check if this request is a hash uploaded from a file
         * @param {string}  requestSource  The generation type
         * @returns  {boolean}  True if uploaded hash false otherwise
         */
        function isHashSource(requestSource) {
            return isBrowserHash(requestSource) || isHashUpload(requestSource);
        }

		return {
			subjectParse: fxAppViewService.subjectParse,
			subjectToString: fxAppViewService.subjectToString,
			prepareCsr: prepareCsr,
			ISOTimetoFXTime: fxAppViewService.ISOTimetoFXTime,
			getAllExtensions: fxAppViewService.getAllExtensions,
			getProfileExtensionSet: fxAppViewService.getProfileExtensionSet,
			getIssuancePolicies: fxAppViewService.getIssuancePolicies,
			getApprovalGroups: fxAppViewService.getApprovalGroups,
			getSigningCerts: fxAppViewService.getSigningCerts,
			getDNProfilesAsFormData: fxAppViewService.getDNProfilesAsFormData,
            hexDecode: fxAppViewService.hexDecode,
            handleFileHash: handleFileHash,
            handleRequestFile: handleRequestFile,
            isBrowserHash: isBrowserHash,
            isHashSource: isHashSource,
            isHashUpload: isHashUpload,
            isPEM: fxAppViewService.isPEM,
            pickRequest: pickRequest,
            readHashFromFile: readHashFromFile,
			selectApprovalGroup: selectApprovalGroup,
			selectIssuancePolicy: selectIssuancePolicy,
			selectSigningCert: selectSigningCert,
            setFormFromCSR: setFormFromCSR,
            slowPromise: fxAppViewService.slowPromise,
			validateCsr: fxAppViewService.validateCsr,
			clientValidateCsr: fxAppViewService.clientValidateCsr,
			submitCsr: submitCsr,
			getFormDataFromUploadedCsr: fxAppViewService.getFormDataFromUploadedCsr,
			getFirstInnerObj: fxAppViewService.getFirstInnerObj,
			getFirstInnerValue: fxAppViewService.getFirstInnerValue,
			getObjKeys: fxAppViewService.getObjKeys,
			keyTypeDefs: fxAppViewService.keyTypeDefs,
			keyTypeStringToFormParams: fxAppViewService.keyTypeStringToFormParams,
			determineInitialKeyTypeValue: fxAppViewService.determineInitialKeyTypeValue,
			getFormSteps: getFormSteps,
			generateCSR: generateCSR,
			checkCustomOID: fxAppViewService.checkCustomOID,
			updateASN1Preview: fxAppViewService.updateASN1Preview,
			updateExtensionValues: fxAppViewService.updateExtensionValues,
			addItemToExtension: fxAppViewService.addItemToExtension,
			removeItemFromExtension: fxAppViewService.removeItemFromExtension,
			sortExtOptions: fxAppViewService.sortExtOptions,
			removeDuplicateOptions: fxAppViewService.removeDuplicateOptions,
			addExtension: fxAppViewService.addExtension,
			removeExtension: fxAppViewService.removeExtension,
			isExtensionDisabled: fxAppViewService.isExtensionDisabled,
            emailRegex: fxAppViewService.emailRegex,
            updateIssuanceApprovalGroup: updateIssuanceApprovalGroup,
		};
	}]
);
