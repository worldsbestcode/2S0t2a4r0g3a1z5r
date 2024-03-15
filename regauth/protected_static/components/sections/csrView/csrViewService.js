/**
 * Provides commonly used functions for the CSR view
 *
 * @returns {object}    helper functions injected into the CSR view controller
 */
var csrViewService = fxApp.factory('csrViewService',
    ['$http', '$q', '$timeout', 'filterService', 'fxAppService', 'fxAppFilterService',
     'fxAppViewService', 'fxAppModalService',
    function($http, $q, $timeout, filterService, fxAppService, fxAppFilterService,
             fxAppViewService, fxAppModalService) {
        var viewType = 'APPROVABLE_OBJ';

        /**
         * Check the object is a hash
         * @param {object}  data - Object data
         * @returns {boolean}  True if it is a object signature request
         */
        function isHash(data) {
            return data.objectType === 'SIGNABLE_OBJ';
        }

        /**
         * Check the object is a CSR
         * @param {object}  data - Object data
         * @returns {boolean}  True if it is a CSR
         */
        function isCSR(data) {
            return data.objectType === 'CERT_REQ';
        }

		/**
		 * Update or approve/deny a CERT_REQ
		 *
		 * @param   {object}    csr       - the certificate signing request
		 * @param   {string}    newStatus - Approved or Denied
		 * @param   {string}    message   - Approve/Deny message
		 * @returns {promise}   resolved upon receiving the response
		 */
		function updateCsr(csr, newStatus, message) {
			var deferred = $q.defer();

            var objectType = csr.objectType;
			if (newStatus === "Approved" || newStatus === "Denied") {

                var csrUpdateQuery = { "objectData": {} };
                csrUpdateQuery.objectData[objectType] = [csr];

				// If there are no previous signing approvals, we do an update first
				// because the user can change the CSR. If there are existing approvals,
				// don't do an update first because the server will reject it.
				if (csr.signingApprovals.length) {
					approveDenyCsr(csr, newStatus, message, deferred);
				} else {
					$http.put(window.apipath('/object'), csrUpdateQuery).success(function(data) {
						approveDenyCsr(csr, newStatus, message, deferred);
					});
				}
			} else {
                var csrUpdateQuery = { "objectData": {} };
                csrUpdateQuery.objectData[objectType] = [csr];

				$http.put(window.apipath('/object'), csrUpdateQuery).success(function(data) {
					deferred.resolve(data);
				});
			}

			return deferred.promise;
		}

		/**
		 * Sends a CSR to the middleware for approval/denial.
		 * 
		 * @param {object} csr CSR to send.
		 * @param {string} newStatus Whether to approve or deny the CSR.
		 * @param {string} message Optional approve/deny message.
		 * @param {any} deferred Deferred callback.
		 */
		function approveDenyCsr(csr, newStatus, message, deferred) {

            var objectType = csr.objectType;
			var loginData = fxAppService.getLoginData();

			var csrApproveQuery = {
				"method": "create",
				"approveData": {}
			};

			// build the signing approval JSON
			var signingApproval = {
				"approvalTime": fxAppViewService.ISOTimetoFXTime(new Date().toISOString()),
				"approved": newStatus === "Approved",
				"message": message ? message : "",
				"userId": loginData.primaryIdentity.id,
				"userName": loginData.primaryIdentity.name,
			};

            var idType = isCSR(csr) ? 'csrID' : 'hashID';
            signingApproval[idType] = csr.objectID;

			// add it to the query
			csrApproveQuery.approveData[objectType] = [signingApproval];

			// send the approval
			$http.post(window.apipath('/approve'), csrApproveQuery).success(function (data) {
				deferred.resolve(data);
			});
		}

		/**
		 * Renews a CSR on the server.
		 * 
		 * @param {object} csr CSR to renew.
		 */
		function renewCsr(csr) {

			var deferred = $q.defer();
            var objectID = csr.objectID;

			var csrRenewQuery = {
				"renewData": {
					"id": objectID
				}
			};

			// send the approval
			$http.post(window.apipath('/renew'), csrRenewQuery).success(function (data) {
				deferred.resolve(data);
			});

			return deferred.promise;
		}
		/**
		 * Converts a CERT_REQ back into its original format in preparation for
		 * sending it in a request
		 *
		 * @param   {object}    csr - the certificate signing request
		 * @returns {object}    a CERT_REQ in its original format
		 */
		function prepareCsr(csr) {
			// Copy the form data
			var preparedCsr = JSON.parse(JSON.stringify(csr));

            if (isCSR(csr)) {
                // Set the DN
                preparedCsr.subject = fxAppViewService.subjectToString(
                    fxAppViewService.maskDNWithProfile(preparedCsr)
				);
				
				var uniqueExts = [];

				if (csr.profileOverride === true) {

					// Add the profile extensions, overriding the user's data where OIDs conflcit.
					for (var i = 0; i < preparedCsr.v3Extensions.length; ++i) {

						var oid = preparedCsr.v3Extensions[i].oid;
						uniqueExts.push(preparedCsr.v3Extensions[i]);
					}

					var profileOIDs = preparedCsr.v3Extensions.map(function (a) { return a.oid; });
					var allowUserDefined = csr.extensionProfileData.allowUserDefined;

					// Add the user's extensions, unless the selected profile doesn't allow
					// custom extensions (ones outside the profile's list).
					for (var i = 0; i < preparedCsr.v3CertExtensions.length; ++i) {
						var oid = preparedCsr.v3CertExtensions[i].oid;

						if (!allowUserDefined && !profileOIDs.includes(oid)) {
							continue;
						}

						if (!profileOIDs.includes(oid)) {
							uniqueExts.push(preparedCsr.v3CertExtensions[i]);
						}
					}
				} 
				else {
                    // Update cert extension with customFormData
                    fxAppViewService.updateExtensionValues(preparedCsr.v3CertExtensions);
					uniqueExts = preparedCsr.v3CertExtensions;
				}

                // set the extensions
				preparedCsr.v3ExtensionDesc = fxAppViewService.createExtensionDescriptions(uniqueExts);
				preparedCsr.v3Extensions = fxAppViewService.createV3ExtensionsString(uniqueExts);
            }

			// Set other fields
			preparedCsr.emails = fxAppViewService.strToCSV(csr.emails);

			// set the key type if using generated PKI
			if (csr.isGeneratedPKI) {
				preparedCsr.keyType = fxAppViewService.keyTypeToString(
					fxAppViewService.getObjKeys(csr.keyTypeSelected)[0],
					csr.keyTypeSelectedSize
				);
			}

			return preparedCsr;
		}

		/**
		 * Modify the JSON data of a CERT_REQ to be in the format that the
		 * CSR view form expects
		 *
		 * @param   {object}    csr - the certificate signing request
		 * @returns {object}    a CERT_REQ in its original format
		 */
		function unprepareCsr(csr) {

			csr.status = fxAppViewService.capitalizeFirstLetter(csr.status);
            if (csr.subject) {
                csr.subject = fxAppViewService.subjectParse(csr.subject);
            }

			return csr;
		}

		/**
		 * Gets the filter string representation of the current view selected
		 *
		 * @returns {string}    the filter string
		 */
		function getFilter() {
			var viewToDisplay = fxAppService.getView();
			var views = fxAppService.getViews();

			if (viewToDisplay === views['csrViewPending']) {
				return "Pending";
			}
			else if (viewToDisplay === views['csrViewSigned']) {
				return "Signed";
			}
			else if (viewToDisplay === views['csrViewDenied']) {
				return "Denied";
			}
			else {
				return "";
			}
		}

		/**
		 * Converts an iterable object of ID-name pairs into an array of objects
		 *
		 * @param   {array}    profiles - iterable object
		 * @returns {array}    array of objects
		 */
		function IDNameToObjArray(profiles) {
			return Object.keys(profiles).map(function(item) {
				return {
					id: item,
					name: profiles[item]
				};
			});
		}

		/**
		 * Returns the labels required to find which branch was selected before
		 * the tree was updated with new data
		 *
		 * @param   {object}     treeControl - contains tree control callbacks
		 * @param   {boolean}    trackChild  - whether to select the child branch
		 * @returns {object}     the saved state of the tree
		 */
		function createTreeState(treeControl, trackChild) {
			var selectedBranch =  treeControl.get_selected_branch();
			var parentBranch = treeControl.get_parent_branch(selectedBranch);

			if (trackChild) {
				return {
					parentLabel: parentBranch.label,
					childLabel: selectedBranch.label
				};
			}
			else {
				return {
					parentLabel: parentBranch.label,
					childLabel: ''
				};
			}
		}

		/**
		 * Select a branch from the tree
		 *
		 * @param   {object}    treeControl - contains tree control callbacks
		 * @param   {object}    config      - the branch and a sequence of tree manipulations
		 */
		function selectBranch(treeControl, config) {

			// branch was specified
			if (config.branch) {
				treeControl.select_branch(config.branch);
			}

			// branch was not specified
			else {

				// clear selected branch
				treeControl.select_branch();
			}

			// options were specified
			if (config.options) {

				// sequentially apply options
				config.options.map(function(option) {

					if (option === 'select_first_branch') {
						treeControl.select_first_branch();
					}
					else if (option === 'expand_all') {
						treeControl.expand_all();
					}
					else if (option === 'collapse_all') {
						treeControl.collapse_all();
					}
					else if (option === 'expand_branch') {
						treeControl.expand_branch();
					}
				});
			}
		}

		/**
		 * Creates the default clauses for the view
		 * @returns {Array}  The default clauses
		 */
		function defaultClauses() {
			var statusValue = getFilter().toLowerCase();

			if (statusValue === '') {
				return [];
			}
			else {
				return [
					filterService.valueClause('Approvable Object', 'Status', statusValue)
				];
			}
		}

		/**
		 * Makes a filter request for the current view
		 *
		 * @param   {object}      scope - the csr view controller scope
		 * @param   {array}       clauses - optional list of filter clauses
		 * @param   {function}    callback - optional callback when done
		 */
		function getTreeForView(scope, clauses, callback) {
			var options = fxAppFilterService.getOptions();
			var query = clauses || defaultClauses();

            if (fxAppService.isAnonymous() && !clauses) {
                fxAppService.resetLoading();
                fxAppFilterService.clearClauses()
                fxAppFilterService.showModal(null, callback);
                return;
            }

			fxAppViewService.getFilterResults(
				viewType,
				"RESULTS",
				query,
				options
			).then(function(results) {
				scope.fxAppTreeService.paginationData.pageCount = 0;

                if (results.hasOwnProperty('error')) {
                    fxAppModalService.showModal('Retrieve Error', results.error);
                    return;
                }

				if (results.parentIDs.length) {
					// Filter the returned results
					fxAppViewService.getApprovalGroups(results.parentIDs).then(function(groups) {
						// Set the approval groups and cert requests
						scope.approvalGroups = groups;
                        scope.fxAppTreeService.paginationData.filterCount = results.matchCount;
                        scope.fxAppTreeService.paginationData.pageCount = results.children.length;
						scope.certRequestsFromFilter = results.children.map(function(csr) {
							return unprepareCsr(csr);
						});
					})
				} else {
                    // If no results returned, set everything to empty values
                    scope.approvalGroups = [];
                    scope.fxAppTreeService.paginationData.filterCount = 0;
                    scope.certRequestsFromFilter = [];
                }
            }).finally(function () {
                fxAppService.resetLoading();
                if (callback) {
                    callback();
                }
            });
		}

		/**
		 * Makes a COUNT request for the total count of APPROVABLE_OBJs
		 *
		 * @returns {promise}   resolved upon receiving the response
		 */
		function getApprovableObjectTotalCount() {
			var deferred = $q.defer();

			fxAppViewService.getObjectTotalCount(viewType).then(function(count) {
				deferred.resolve(count);
			});

			return deferred.promise;
		}

		/**
		 * Makes a COUNT request for the count of APPROVABLE_OBJs with a given status
		 *
		 * @param   {string}    status - the status
		 * @returns {promise}   resolved upon receiving the response
		 */
		function getApprovableObjectStatusCount(status) {
			var deferred = $q.defer();

			var options = {
				criteria: {
					'Approvable Object': filterService.schema.approvableObject()
				}
			};

			fxAppViewService.getFilterResults(
				viewType,
				'COUNT',
				[filterService.valueClause('Approvable Object', 'Status', status)],
				options
			).then(function(count) {
				deferred.resolve(count);
			});

			return deferred.promise;
		}

		/**
		 * Makes a COUNT request for Pending, Signed, and Denied APPROVABLE_OBJs
		 *
		 * @returns {promise}   resolved upon receiving the response
		 */
		function getPendingSignedDeniedCounts() {
			var deferred = $q.defer();

			async.parallel([
				function(callback) {
					getApprovableObjectStatusCount('pending').then(function(count) {
						callback(null, count);
					});
				},
				function(callback) {
					getApprovableObjectStatusCount('signed').then(function(count) {
						callback(null, count);
					});
				},
				function(callback) {
					getApprovableObjectStatusCount('denied').then(function(count) {
						callback(null, count);
					});
				},
			], function(error, results) {
				deferred.resolve({
					pending: results[0],
					signed: results[1],
					denied: results[2]
				});
			});

			return deferred.promise;
		}

		function setupFilter(scope) {

            /**
             * Properties of certificate request object
             * @returns {object}  Filter properties of certificate request
             */
            function makeApprovable(objectType) {
                var approvable = filterService.schema.approvableObject();
                delete approvable['Type'];

                var csr = filterService.objectFieldSchema(objectType);
                for (var i in csr) {
                    approvable[i] = csr[i];
                }

                return approvable;
            }

            var criteria = {
                'Approval Group': filterService.schema.approvalGroup(),
                'Certificate Request': makeApprovable('CERT_REQ'),
                'Approvable Object': filterService.schema.approvableObject(),
                'Signable Object': makeApprovable('SIGNABLE_OBJ'),
                'Signing Approvers': filterService.schema.signingApprover()
            };

            var clauseCondition = ['And', 'Or', 'Not'];
            if (fxAppService.isAnonymous()) {
                clauseCondition = ['And', 'Or'];
                criteria = filterService.anonymousCriteria();
            }

			scope.fxAppFilterService.setOptions({
                clauseCondition: clauseCondition,
                criteria: criteria
			});
		}

		/**
		 * Called when "Inject Into Smart Token" is clicked.
		 */
		function injectIntoSmartToken(formData) {

			var fxcng = fxAppService.getFXCNGPlugin();

			var alert_title = "";
			var alert_message = "";

			document.body.style.cursor = 'wait';

			// There is a 500ms delay to give the browser some time
			// to apply the cursor change.
			$timeout(function() {

				var ok = false;

				if (fxcng) {
					ok = fxcng.injectCertificate(formData.token_provider_name, 
												 formData.token_key_name, 
												 formData.signedCert);
				}

				return ok;

			}, 500).then (function(ok) {

				document.body.style.cursor = 'default';

				if (!ok) {
					alert_title = "Error";
					alert_message = "Smart token injection failed.";
				} else {
					alert_title = "Success";
					alert_message = "Smart token injection succeeded.";
				}

				fxAppModalService.showModal(alert_title, alert_message);
			});
		}

		/**
		 * Produce an array of cert requests from the tree data
		 *
		 * @param     {object}    treeData - the data stored in the tree sidebar
		 * @returns   {array}     array of cert requests
		 */
		function getCertRequestsFromTreeData(treeData) {
			// Iterate every approval group
			return treeData.map(function(approvalGroup) {
				// Iterate every cert request
				return approvalGroup.children.map(function(certRequest) {
					// Extract the cert request data used for the form
					return certRequest.value;
				});
			// Unnest the resulting arrays
			}).reduce(function(approvalGroups, approvalGroup) {
				return approvalGroups.concat(approvalGroup);
			});
		}

		/**
		 * Generate HTML from an array of cert requests and an array of columns
		 *
		 * @param     {array}     certRequests - currently loaded cert requests
		 * @param     {array}     columns      - array of column names
		 * @returns   {string}    HTML file
		 */
		function exportCertRequestsToHTML(certRequests, columns) {
			// Document tags
			var htmlOpen = '<html>';
			var htmlClose = '</html>';
			var headOpen = '<head>';
			var headClose = '</head>';
			var bodyOpen = '<body>';
			var bodyClose = '</body>';

			// Table tags
			var tableOpen = '<table>';
			var tableClose = '</table>';
			var theadOpen = '<thead>';
			var theadClose = '</thead>';
			var tbodyOpen = '<tbody>';
			var tbodyClose = '</tbody>';
			var thOpen = '<th>';
			var thClose = '</th>';
			var trOpen = '<tr>';
			var trClose = '</tr>';
			var tdOpen = '<td>';
			var tdClose = '</td>';

			// Document
			var documentOpen = htmlOpen + headOpen + headClose + bodyOpen;
			var documentClose = bodyClose + htmlClose;

			// Table heading
			var tableColumns = columns.map(function(column) {
				return thOpen + column + thClose;
			});
			var tableHeading = theadOpen + trOpen + tableColumns.join('') + trClose + theadClose;

			// Table
			var mainTableOpen = tableOpen + tableHeading + tbodyOpen;
			var mainTableClose = tbodyClose + tableClose;
			var beforeRows = documentOpen + mainTableOpen;
			var afterRows = mainTableClose + documentClose;

			// Generate the HTML document
			return beforeRows + certRequests.map(function(certRequest) {
				return trOpen
				+ tdOpen + certRequest.name + tdClose
				+ tdOpen + certRequest.status + tdClose
				+ tdOpen + certRequest.loadTime + tdClose
				+ tdOpen + certRequest.uploaderName + tdClose
				+ tdOpen + certRequest.notes + tdClose
				+ tdOpen + certRequest.emails + tdClose
				+ tdOpen + (certRequest.isGeneratedPKI ? 'Yes' : 'No') + tdClose
				+ tdOpen + certRequest.v3ExtNames + tdClose
				+ tdOpen + certRequest.expiration + tdClose
				+ tdOpen + certRequest.keyType + tdClose
				+ tdOpen + certRequest.hashAlgorithm + tdClose
				+ trClose;
			}).join('') + afterRows;
		}

		/**
		 * Generate CSV from an array of cert requests and an array of columns
		 *
		 * @param     {array}     certRequests - currently loaded cert requests
		 * @param     {array}     columns      - array of column names
		 * @returns   {string}    CSV file
		 */
		function exportCertRequestsToCSV(certRequests, columns) {
			return columns.join(',') + '\n' + certRequests.map(function(certRequest) {
				return '"' + certRequest.name + '"'
				+ ',' + '"' + certRequest.status + '"'
				+ ',' + '"' + certRequest.loadTime + '"'
				+ ',' + '"' + certRequest.uploaderName + '"'
				+ ',' + '"' + certRequest.notes + '"'
				+ ',' + '"' + certRequest.emails + '"'
				+ ',' + '"' + (certRequest.isGeneratedPKI ? 'Yes' : 'No') + '"'
				+ ',' + '"' + certRequest.v3ExtNames + '"'
				+ ',' + '"' + certRequest.expiration + '"'
				+ ',' + '"' + certRequest.keyType + '"'
				+ ',' + '"' + certRequest.hashAlgorithm + '"';
			}).join('\n');
		}

		/**
		 * Generate a file from the tree data and specified file type
		 *
		 * @param     {array}     treeData - the data stored in the tree sidebar
		 * @param     {string}    format   - file type
		 * @returns   {string}    file string to be downloaded
		 */
		function exportSearchResults(treeData, format) {
			// Get the cert requests
			var certRequests = getCertRequestsFromTreeData(treeData);
			var columns = [
				'Name',
				'Status',
				'Load Time',
				'Uploader',
				'Notes',
				'Emails',
				'Use Generated PKI',
				'V3 Extension Names',
				'Expiration',
				'Key Type',
				'Hash Algorithm'
			];

			// Generate the file
			if (format === "HTML") {
				return exportCertRequestsToHTML(certRequests, columns);
			}
			else if (format === "CSV") {
				return exportCertRequestsToCSV(certRequests, columns);
			}

			return '';
		}

		/**
		 * Check if DN field should be displayed for the selected profile
		 *
		 * @param     {object}    formdata     - CSR form data
		 * @param     {string}    profileOID   - DN profile OID
		 * @param     {string}    extensionOID - DN extension OID
		 * @returns   {boolean}   whether DN field should be displayed
		 */
		function shouldDisplayDNExtension(formdata, profileOID, extensionOID) {
			var profileIsNone = formdata.selectedDNProfile.name === 'None';
			var subjectHasOID = formdata.subject[extensionOID] !== undefined;
			var profileHasOID = profileOID === extensionOID;

			if (profileIsNone) {
				return subjectHasOID && profileHasOID;
			}
			else {
				return profileHasOID;
			}
		}

		/**
		 * Check if the CSR form field should be disabled according to
		 * the permissions and the selected CSR's status
		 *
		 * @param     {object}   csr        - Data of the selected CSR.
		 * @param     {object}   permissions - Permissions of the user group.
		 * @param     {boolean}  ignoreMultipleApprovals Whether we're ignoring the 
		 * 						 fact that there are existing approvals in the CSR.
		 * @returns   {object}   returns the value string when true, null otherwise
		 *                       see https://www.w3.org/TR/html5/disabled-elements.html
		 *                       for info on "actually disabled" elements
		 */
		function permissionsShouldDisableField(csr, permissions, ignoreMultipleApprovals) {
			// Only enable when the status is "Pending" and the user is a vetter,
			// and if there are zero existing signing approvals and we're not ignoring the
			// fact that there might be some.
		
			if (csr.status != 'Pending') {
				return 'true';
			} else if (!permissions.vetter) {
				return 'true';
			} else if (csr.signingApprovals.length && !ignoreMultipleApprovals) {
				return 'true';
			} else {
				return null;
			}
		}

        function setCrlFromCertificate(signingCrl, target) {
            /**
             * Set the CRL data using the form data
             * @param {Array}  crls - The crl list
             */
            function setCRL(crls) {
                target.certCrl = crls[0];
            }

            if (signingCrl !== '0') {
                fxAppViewService.getObjects('CRL', [signingCrl]).then(setCRL);
            } else {
                setCRL([null]);
            }
        }

        var revokeReasons = {
            0: 'Unspecified',
            1: 'Key Compromise',
            2: 'CA Compromise',
            3: 'Affiliation Changed',
            4: 'Superseded',
            5: 'Cessation of Operation',
            6: 'Certificate Hold',
            8: 'RemoveFromCRL',
            9: 'Privilege Withdrawn',
            10: 'AA Compromise',
        };

		return {
			subjectParse: fxAppViewService.subjectParse,
			subjectToString: fxAppViewService.subjectToString,
			ISOTimetoFXTime: fxAppViewService.ISOTimetoFXTime,
			getFilterResults: fxAppViewService.getFilterResults,
			getApprovalGroups: fxAppViewService.getApprovalGroups,
			getSigningCerts: fxAppViewService.getSigningCerts,
			getIssuancePolicies: fxAppViewService.getIssuancePolicies,
			getApprovableObjectTotalCount: getApprovableObjectTotalCount,
			getPendingSignedDeniedCounts: getPendingSignedDeniedCounts,
			getAllExtensions: fxAppViewService.getAllExtensions,
			getProfileExtensionSet: fxAppViewService.getProfileExtensionSet,
			getCertExtensionSet: fxAppViewService.getCertExtensionSet,
			getDNProfilesAsFormData: fxAppViewService.getDNProfilesAsFormData,
			removeDuplicateOptions: fxAppViewService.removeDuplicateOptions,
			updateExtensionValues: fxAppViewService.updateExtensionValues,
			sortExtOptions: fxAppViewService.sortExtOptions,
			convertV3ExtensionsStringToArrayOfObjects: fxAppViewService.convertV3ExtensionsStringToArrayOfObjects,
			addExtension: fxAppViewService.addExtension,
			removeExtension: fxAppViewService.removeExtension,
			checkCustomOID: fxAppViewService.checkCustomOID,
            isCSR: isCSR,
			isExtensionDisabled: fxAppViewService.isExtensionDisabled,
            isHash: isHash,
			addItemToExtension: fxAppViewService.addItemToExtension,
			removeItemFromExtension: fxAppViewService.removeItemFromExtension,
			updateASN1Preview: fxAppViewService.updateASN1Preview,
			getTreeForView: getTreeForView,
			setupFilter: setupFilter,
			updateCsr: updateCsr,
			renewCsr: renewCsr,
			validateCsr: fxAppViewService.validateCsr,
			clientValidateCsr: fxAppViewService.clientValidateCsr,
			unprepareCsr: unprepareCsr,
			prepareCsr: prepareCsr,
			getFilter: getFilter,
			IDNameToObjArray: IDNameToObjArray,
			hexToArrayBuffer: fxAppViewService.hexToArrayBuffer,
			downloadString: fxAppViewService.downloadString,
			spacesToUnderscores: fxAppViewService.spacesToUnderscores,
			getFormDataFromUploadedCsr: fxAppViewService.getFormDataFromUploadedCsr,
			createTreeState: createTreeState,
			selectBranch: selectBranch,
			getFirstInnerObj: fxAppViewService.getFirstInnerObj,
			getFirstInnerValue: fxAppViewService.getFirstInnerValue,
			getObjKeys: fxAppViewService.getObjKeys,
			keyTypeDefs: fxAppViewService.keyTypeDefs,
			keyTypeStringToFormParams: fxAppViewService.keyTypeStringToFormParams,
			determineInitialKeyTypeValue: fxAppViewService.determineInitialKeyTypeValue,
			injectIntoSmartToken: injectIntoSmartToken,
			exportSearchResults: exportSearchResults,
			shouldDisplayDNExtension: shouldDisplayDNExtension,
            permissionsShouldDisableField: permissionsShouldDisableField,
            revokeReasons: revokeReasons,
            setCrlFromCertificate: setCrlFromCertificate,
			emailRegex: fxAppViewService.emailRegex
		};
	}]
);
