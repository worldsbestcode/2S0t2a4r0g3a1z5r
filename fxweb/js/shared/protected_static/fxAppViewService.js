/**
 * Provides any functions common to at least two view services
 *
 * @returns {object}    helper functions injected into view services
 */

var fxAppViewService = fxApp.factory('fxAppViewService',
    ['$http', '$q', '$timeout', 'fxAppService', 'fxAppTreeService',
     'fxAppStringService', 'fxAppX509Service', 'fxEncodeService', 'filterService',
    function($http, $q, $timeout, fxAppService, fxAppTreeService,
             fxAppStringService, fxAppX509Service, fxEncodeService, filterService) {

	/**
	 * Makes a request for REG_AUTHs
	 *
	 * @param   {string}     managerName - the name of the primary object type
	 * @param   {array}      objectIDs - the IDs of the primary object type
	 * @returns {promise}    resolved upon receiving the response
	 */
	function getIssuancePolicies(managerName, primaryObjectIDs) {
		var deferred = $q.defer();

		var policyQuery = {
			"method": "retrieve",
            "name": "issuance_policies",
			"formData": {
				"issuance_policies": {
					"manager": managerName,
					"objectID": primaryObjectIDs ? primaryObjectIDs.join(',') : ''
				}
			}
		};

		$http.post(window.apipath('/formdata'), policyQuery).success(function(data) {
			deferred.resolve(data.formData.REG_AUTH.map(function(policy) {
				return JSON.parse(policy);
			}));
		});

		return deferred.promise;
	}

    /**
     * Shows the busy cursor
     */
    function busyCursor () {
        document.body.style.cursor = 'wait';
    }

    /**
     * Shows the normal cursor
     */
    function normalCursor () {
        document.body.style.cursor = 'default';
    }


    /**
     * Sets and removes the wait cursor for long promises
     * @param {function}  promiseCallback  A promise producing function
     * @returns {promise}  the promise result
     */
    function slowPromise(promiseCallback) {
        busyCursor();
        return promiseCallback().finally(normalCursor);
    }

    /**
     * Internal function for getting the filter ordering
     * @returns {object}  An object with ordering data
     */
    function filterOrdering () {
        return filterService.orderingData(fxAppTreeService.pageSize(), fxAppTreeService.index());
    }

	/**
     * Makes a request for any object
	 *
     * @param   {string}    manager - The object type to get
     * @param   {array}     objectIDs - DBIDs of the objects to get
     * @param   {array}     clauses - Filter clauses (optional)
     * @param   {boolean}   unlimitedResults - Whether to limit number of results (optional)
	 * @returns {promise}    resolved upon receiving the response
	 */
     function getObjects(manager, objectIDs, clauses, unlimitedResults) {
		var deferred = $q.defer();
        var ids = {};
        ids[manager] = objectIDs ? objectIDs.join(',') : '';

        var request = filterService.requestData(manager, null, ids);
        var ordering = filterService.orderingData(unlimitedResults ? 0: fxAppTreeService.pageSize());
        var query = filterService.makeFilter(request, ordering, clauses);

        $http.post(window.apipath('/object'), query).success(function(data) {
            deferred.resolve(data.objectData[manager].map(function (obj) {
                return JSON.parse(obj);
			}));
		});

		return deferred.promise;
	}

	/**
	 * Makes a request for APPROVAL_GROUPs
	 *
	 * @param   {array}      objectIDs - the object IDs of the APPROVAL_GROUPs
	 * @returns {promise}    resolved upon receiving the response
	 */
	function getApprovalGroups(objectIDs) {
        return getObjects('APPROVAL_GROUP', objectIDs, [], true);
    }

	/**
	 * Makes a request for available signing certs
	 *
	 * @returns {promise}   resolved upon receiving the response
	 */
	function getSigningCerts(objectIDs) {
        const moType = 'X.509 certificate'
        // Checks certificate for policy ID, not expired, and is not revoked
        let clauses = [
            filterService.createFullClause(moType, 'policy ID', '0', 'AND', 'GREATER_THAN'),
            filterService.createFullClause(moType, 'certificate expiration', moment(), 'AND', 'GREATER_THAN'),
            filterService.createFullClause(moType, 'status', '0'),
        ]

        let promise = getObjects('X509CERT', objectIDs, clauses, true);

        return promise;
    }

	/**
	 * Determine what object type to use given the field name
	 *
	 * @param   {string}    fieldName - The field name
	 * @param   {string}    objectType - The object type 
	 * @returns {string}    the object type to use
	 */
	function getObjectTypeFromFieldName(fieldName, objectType) {
		// The clause options with properly distinguished object types/fields
        var unaliasedOptions = {
            'Approval Group': filterService.schema.approvalGroup(),
            'Approvable Object': filterService.schema.approvableObject(),
            'Certificate Request': filterService.schema.certificateRequest(),
            'Signable Object': filterService.schema.signableObject(),
            'Signing Approvers' : filterService.schema.signingApprover()
        };

		// Find under which object type the field exists
		// (assumes uniqueness of field names)
		for (var unaliasedObjectType in unaliasedOptions) {
            for (field in unaliasedOptions[unaliasedObjectType]) {
				if (field === fieldName && 
                        unaliasedOptions[unaliasedObjectType][field].objectTypes.indexOf(objectType) > -1) { 
                    return unaliasedOptions[unaliasedObjectType][field].baseObjectType;
				}
			}
		}

		return '';
	}

	/**
	 * Performs a filter query
	 *
	 * @param   {string}     managerName - the name of the managed object
	 * @param   {string}     filterType - the name of the filter type
	 * @param   {array}      filterClauses - the filter clauses
	 * @param   {object}     filterOptions - the filter clause options
	 * @returns {promise}    resolved upon receiving the response
	 */
	function getFilterResults(managerName, filterType, filterClauses, filterOptions) {
		var deferred = $q.defer();
        var request = filterService.requestData(managerName, filterType);
        var clauses = filterService.prepareClauses(filterClauses, filterOptions);
        var filterQuery = filterService.makeFilter(request, filterOrdering(), clauses);

		$timeout(function() {
			$http.post(window.apipath('/object'), filterQuery).success(function(data) {
                if (data.result === 'Failure') {
                    data.objectData = {};
                    deferred.resolve({
                        error: data.message
                    });

                    return;
                }

                var children = [];
                var matchCount = -1;
                for (var resultType in data.objectData) {
                    if (resultType === 'LOG_FILTER') {

                        var resultTypeDataArr = data.objectData[resultType];
                        if (resultTypeDataArr.length > 0) {
                            var resultTypeData = JSON.parse(resultTypeDataArr[0]);
                            if ('matchCount' in resultTypeData) {
                                matchCount = resultTypeData['matchCount'];
                            }
                        }
                        continue;
                    }

                    children = children.concat(data.objectData[resultType]);
                }

                children = children.map(function(item) {
                    return JSON.parse(item);
                });

				if (filterType === "RESULTS") {
                    // collect unique parent IDs
                    var parentIDs = removeDuplicates(children.map(function(child) {
                        return child.parentID;
                    }));

                    if (matchCount === -1) {
                        matchCount = children.length;
                    }

					deferred.resolve({
						parentIDs: parentIDs,
						children: children,
						matchCount: matchCount
					});
				}

				else if (filterType === "COUNT") {
					deferred.resolve(children[0].count);
				}
			});
		}, 500);

		return deferred.promise;
	}

    /**
     * Get a list of all the device results of every type
     * @param {array}  typeList  A list of managed types to retrieve
     */
    function getAllObjectsForTypes(typeList) {
        var typeResults = [];

        /**
         * Process each individual type result
         * @param {object}  results  An object containing filter results
         * @return {promise}  A promise completed after joining the type results
         */
        function processTypeResult(objectType, results) {
            if (results.hasOwnProperty('error')) {
                console.error('Failed to retrieve "%s": %s', objectType, results.error);
                fxAppModalService.showModal('Retrieve Error', results.error);
            } else {
                typeResults = typeResults.concat(results.children);
            }
        }

        function getTypeResult(objectType) {
            var promise = getFilterResults(objectType, 'RESULTS', [], {});
            return promise.then(function (results) { processTypeResult(objectType, results); });
        }

        var promises = typeList.map(function (objectType) { return getTypeResult(objectType); });

        if (promises.length > 0) {
            return $q.all(promises).then(function () { return typeResults; });
        } else {
            console.error('Failed to process type result for "%s".', objectType);
            return $q.reject('Could not process type results');
        }
        return ;
    }

	/**
	 * Get the total count of a managed object
	 *
	 * @param   {string}     managerName - the name of the managed object
	 * @returns {promise}    resolved upon receiving the response
	 */
	function getObjectTotalCount(managerName) {
		var deferred = $q.defer();

		getFilterResults(
			managerName,
			"COUNT",
			[],
			[]
		).then(function(count) {
			deferred.resolve(count);
		});

		return deferred.promise;
	}

	/**
	 * Gets the extension set of a selected profile
	 *
	 * @param   {string}     profileID - the ID of the selected profile
	 * @param   {string}     certID    - the ID of the selected signing cert
	 * @returns {promise}    resolved upon receiving the response
	 */
	function getProfileExtensionSet(profileID, certID) {
		var deferred = $q.defer();

		var extSetQuery = {
			"method": "retrieve",
            "name": "v3_extensions_per_profile",
			"formData": {
				"v3_extensions_per_profile": {
					"objectID": certID
				}
			}
		};

        var empty = { extensions: [], profile: {} };
		if (profileID && certID) {
			$http.post(window.apipath('/formdata'), extSetQuery).success(function(data) {
				// check if V3EXT_PROFILE has any elements
                if (data.formData.V3EXT_PROFILE && data.formData.V3EXT_PROFILE.length > 0) {
					var profileObject = data.formData.V3EXT_PROFILE.map(function(profile) {
						return JSON.parse(profile);
          }).filter(function (profile) {
            return profile && profile.objectID === profileID;
					})[0];

					deferred.resolve({
						extensions: fxAppX509Service.convertV3ExtensionsStringToArrayOfObjects(
							profileObject.v3Extensions,
							profileObject.v3ExtensionDesc
						),
						profile: profileObject
					});
				}

				// V3EXT_PROFILE is empty (probably don't have permissions to retrieve the profile)
				else {
					deferred.resolve(empty);
				}
			});
		}

		else {
			deferred.resolve(empty);
		}

		return deferred.promise;
	}
	
	/**
	 * Gets the extension set of a selected CSR.
	 *
	 * @param   {string}     csrID    - the ID of the selected CSR.
	 * @returns {promise}    Resolved upon receiving the response.
	 */
	function getCertExtensionSet(csrID) {
		var deferred = $q.defer();

		var extSetQuery = {
			"method": "retrieve",
            "name": "v3_extensions_per_cert",
			"formData": {
				"v3_extensions_per_cert": {
					"objectID": csrID
				}
			}
		};

		var empty = { extensions: [], profile: {} };
		if (csrID) {
			$http.post(window.apipath('/formdata'), extSetQuery).success(function (data) {

				if (data.formData.V3EXT_PROFILE && data.formData.V3EXT_PROFILE.length > 0) {
					var profileObject = data.formData.V3EXT_PROFILE.map(function (profile) {
						return JSON.parse(profile);
					})

					// I only expect one "profile", since it will hold all the extensions in the CSR.
					deferred.resolve({
						extensions: fxAppX509Service.convertV3ExtensionsStringToArrayOfObjects(
							profileObject[0].v3Extensions,
							profileObject[0].v3ExtensionDesc
						),
						profile: profileObject
					});
				}

				else {
					deferred.resolve(empty);
				}
			});
		}

		else {
			deferred.resolve(empty);
		}

		return deferred.promise;
	}

	/**
	 * Gets all DN profiles available to the user logged in
	 *
	 * @returns {promise}    resolved upon receiving the response
	 */
	function getDNProfiles() {
		var deferred = $q.defer();

		var profileQuery = {
			"method": "retrieve",
			"objectType": "Filter",
			"quantity": 1000,
			"request": {
				"manager": "X509DN_PROFILE",
				"chunk": 0,
				"chunkSize": 1000,
				"chunkCount": 1,
				"matchCount": 1,
				"flags": [],
				"filterType": "RESULTS",
				"sortAscending": false,
				"distinctOn": "",
				"objectIDs": {}
			}
		};

		$http.post(window.apipath('/object'), profileQuery).success(function(data) {
			deferred.resolve(data.objectData.X509DN_PROFILE.map(function(profile) {
				return JSON.parse(profile);
			}));
		});

		return deferred.promise;
	}

	/**
	 * Gets all DN profiles in the format the view expects
	 *
	 * @param   {array}      defaultProfiles - array of default profile names
	 * @returns {promise}    resolved upon receiving the response
	 */
	function getDNProfilesAsFormData(defaultProfiles) {
		var deferred = $q.defer();

		getDNProfiles().then(function(profiles) {
			// Add the default profiles
			var result = [];
			defaultProfiles.map(function(profileName) {
				result.push({
					name: profileName,
					extensions: fxAppX509Service.getKnownDNProfile(profileName)
				});
			});

			// Add the other available profiles
			result = result.concat(profiles.map(function(profile) {
				return {
					name: profile.name,
					extensions: fxAppX509Service.subjectParse(profile.extensions)
				};
			}));

			deferred.resolve(result);
		});

		return deferred.promise;
	}

	/**
	 * Validates a certificate signing request on the client side
	 *
	 * @param   {object}     csr - the certificate signing request
	 * @returns {promise}    resolved upon receiving the response
	 */
	function clientValidateCsr(csr) {
		var deferred = $q.defer();

		// Check the CSV of emails
		if (csr.emails && !fxAppStringService.regexForCSV(csr.emails, fxAppStringService.emailRegex())) {
			deferred.reject('Emails are invalid');
		}
		else {
			deferred.resolve('');
		}

		return deferred.promise;
	}

	/**
	 * Validates a certificate signing request
	 *
	 * @param   {object}     csr - the certificate signing request
	 * @returns {promise}    resolved upon receiving the response
	 */
	function validateCsr(csr) {
		var deferred = $q.defer();

		var csrValidateQuery = {
			"method": "validate",
            "objectData": {}
		};

        csrValidateQuery.objectData[csr.objectType] = [csr];

		$http.post(window.apipath('/object'), csrValidateQuery).success(function(data) {
			if (data.objectData.result) {
				deferred.resolve(data);
			}
			else {
				deferred.reject(data);
			}
		});

		return deferred.promise;
	}

	/**
	 * Populates DN, hash, and key type by parsing the uploaded request server-side
	 *
	 * @param   {object}     filestring - hex-encoded file
	 * @returns {promise}    resolved upon receiving the response
	 */
	function getFormDataFromUploadedCsr(filestring) {
		var deferred = $q.defer();

		var dnFromCsrQuery = {
			"method": "retrieve",
            "name": "csr_upload",
			"formData": { "csr_upload": {} }
		};

		// parseCSR is always true here because this is called when we upload the
		// CSR to parse it- we haven't submitted yet. After it is submitted, we no
		// longer want to parse the CSR for the DN, because the DN can be changed
		// outside the CSR.
		dnFromCsrQuery.formData.csr_upload['request'] = filestring;
		dnFromCsrQuery.formData.csr_upload['parseCSR'] = true;

		$http.post(window.apipath('/formdata'), dnFromCsrQuery).success(function(data) {
			deferred.resolve(JSON.parse(data.formData.csr_upload[0]));
		});

		return deferred.promise;
	}

    function ldapAuth(policyID, ldapUsername, ldapPassword) {
        var deferred = $q.defer();
        var ldapAuthQuery = {
            'method': 'retrieve',
            'formData': { 'ldap_auth': {} }
        };

        ldapAuthQuery.formData.ldap_auth['policyID'] = policyID;
        ldapAuthQuery.formData.ldap_auth['ldapUsername'] = ldapUsername;
        ldapAuthQuery.formData.ldap_auth['ldapPassword'] = ldapPassword;

        $http.post(window.apipath('/formdata'), ldapAuthQuery).success(function(data) {
            deferred.resolve(data);
        });

        return deferred.promise
    }


	/**
	 * Gets first inner object from an object of objects including the key
	 * (for when "myObj[Object.keys(myObj)[0]]" isn't what you want and
	 *  you understand that JavaScript objects are iterable, but unordered)
	 *
	 * @param   {object}    obj - object containing at least one inner object
	 * @returns {object}    the inner object
	 */
	function getFirstInnerObj(obj) {
		if (obj && typeof obj === "object") {
			var innerObj = {};
			var k = Object.keys(obj)[0];
			var v = obj[k];

			innerObj[k] = v;

			return innerObj;
		}
	}

	/**
	 * Gets first inner value from an object of objects
	 *
	 * @param   {object}    obj - object containing at least one inner object
	 * @returns {object}    the inner value
	 */
	function getFirstInnerValue(obj) {
		if (obj && typeof obj === "object") {
			var k = Object.keys(obj)[0];
			return obj[k];
		}
	}

	/**
	 * Get array of keys as strings
	 *
	 * @param   {object}    obj - object containing at least one key
	 * @returns {string}    the array of keys
	 */
	function getObjKeys(obj) {
		return Object.keys(obj);
	}

	/**
	 * Key type definitions
	 *
	 * @returns {object}    key type definitions
	 */
	function keyTypeDefs() {
		return {
			defaultSizes: {
				RSA: 2048,
				ECC: 384,
				DES: 128,
				AES: 192
			}
		};
	}

	/**
	 * Create key type string
	 *
	 * @param   {string}     name - name of the key type
	 * @param   {integer}    size - size of the key in bits
	 * @returns {string}     key type string
	 */
	function keyTypeToString(name, size) {
		return name + ' ' + size.toString();
	}

	/**
	 * Convert key type string to form parameters
	 *
	 * @param   {string}    keyType - the key type in string format
	 * @param   {object}    options - the key type options from the parent
	 * @returns {object}    key type form parameters
	 */
	function keyTypeStringToFormParams(keyType, options) {
		var keyTypeParams = {
			keyTypeSelected: {},
			keyTypeSelectedSize: 0
		};

		if (keyType && typeof keyType === 'string') {
			// get the name and size
			var keyTypeArr = keyType.split(' ');
			var keyTypeName = keyTypeArr[0];
			var keySize = parseInt(keyTypeArr[1]);

			// set the key type name and base params
			keyTypeParams.keyTypeSelected[keyTypeName] = {
				min: 0, max: 0, step: 1
			};

			// set the selected size
			keyTypeParams.keyTypeSelectedSize = keySize;

			// get the params from the options
			if (options && typeof options === 'object') {
				var params = options[keyTypeName];
				keyTypeParams.keyTypeSelected[keyTypeName] = params;
			}
		}

		return keyTypeParams;
	}

	/**
	 * Determine what the size of the key type should be given the default size
	 * and the restricted maximum size of the key type
	 *
	 * @param   {object}     keyTypeParams - the key type parameters
	 * @param   {integer}    defaultSize   - the default size of the key type
	 * @returns {integer}    the key type size that fits the parameters
	 */
	function determineInitialKeyTypeValue(keyTypeParams, defaultSize) {
		if (defaultSize && keyTypeParams.max >= defaultSize) {
			return defaultSize;
		}
		else {
			return keyTypeParams.max;
		}
	}

	/**
	 * Add an extension's default item to its array of items
	 */
	function addItemToExtension(items, defaultItem) {
		items.push(angular.copy(defaultItem));
	}

	/**
	 * Remove an item from an extension's array of items
	 */
	function removeItemFromExtension(items, index) {
		items.splice(index, 1);
	}

	/**
	 * Sort the array of extension options
	 */
	function sortExtOptions(v3ExtOptions) {
		v3ExtOptions = v3ExtOptions.sort(function(a, b) {
			return a.name.localeCompare(b.name);
		});

		return v3ExtOptions[0];
	}

	/**
	 * Remove duplicates between the extensions
	 * selected and the options available
	 */
	function removeDuplicateOptions(options, selected) {
		if (options && selected) {
			return options.filter(function(option) {
				// Check if this option is already in the array of selected extensions
				// and remove it from the options unless the extension name is 'Custom'
				return (selected.filter(function(selectedExtension) {
					return selectedExtension.oid === option.oid;
				}).length < 1) || option.name === 'Custom';
			});
		}
	}

	/**
	 * Add an extension to the array of selected extensions
	 */
	function addExtension(selectedExtension, formdata) {
		if (selectedExtension) {
			// Add to extensions
			var selectedExtensionCopy = JSON.parse(JSON.stringify(selectedExtension));
			formdata.v3Extensions.push(selectedExtensionCopy);

			// Remove from options unless the extension name is 'Custom'
			if (selectedExtension.name !== 'Custom') {
				var index = formdata.v3ExtOptions.indexOf(selectedExtension);
				formdata.v3ExtOptions.splice(index, 1);
			}
		}
	}

	/**
	 * Remove an extension from the array of selected extensions
	 */
	function removeExtension(selectedExtension, formdata) {
		if (selectedExtension) {
			// Remove from extensions
			var index = formdata.v3Extensions.indexOf(selectedExtension);
			formdata.v3Extensions.splice(index, 1);

			// Add back to options unless the extension name is 'Custom'
			if (selectedExtension.name !== 'Custom') {
				var options = fxAppX509Service.getAllExtensions();
				var foundOptions = options.filter(function(extension) {
					return selectedExtension.name === extension.name;
				});

				if (foundOptions.length > 0) {
					formdata.v3ExtOptions.push(foundOptions[0]);
				}
			}
		}
	}

    /**
     * Function to remove duplicate object from an array
     * @param {Array}  arr - The array to remove duplicates from
     * @returns {Array}  A sorted array without duplicates
     */
    function removeDuplicates(arr) {
        return arr.slice().sort().filter(function (item, pos, arr)  {
            return pos === 0 || item !== arr[pos-1];
        });
    }

	/**
	 * Determine if an extension's form elements should be disabled
	 */
	function isExtensionDisabled(extension, formdata) {
		return extension.mode === 'Fixed' ||
               extension.mode === 'Included' ||
               extension.mode === 'Not Included';
	}

    /**
     * Create a step for a multi step workflow
     *
     * @param {string}  name  The internal step name
     * @param {string}  displayName  The name shown in the GUI
     * @param {function}  validate  The validation function, optional
     * @param {function}  finish  The finish function for any post-step cleanup, optional
     * @returns {object}  A new step
     */
    function createStep(name, displayName, validate, finish) {

        /**
         * Most pages don't need to do anything special when they finish
         *
         * @param {function} updateCallback The callback to update the current page
         */
        function finishFunction(updateCallback) {
            updateCallback();
        }

        return {
            canContinue: false,
            displayName: displayName,
            error: false,
            finish: finish ? finish : finishFunction,
            name: name,
            validate: validate ? validate : function() {
                this.canContinue = true;
            }
        };
    }

    /**
     * Checks if an object properties are all false
     * For an object property to be false all its non object properties must be false
     * @param obj the object to check
     * @return true if all properties are false, false otherwise
     */
    function objectFalse(obj) {
        for (var prop in obj) {
            var val = obj[prop];
            if (typeof(val) === 'object') {
                if (!objectFalse(val)) {
                    return false;
                }
            } else if (val) {
                return false;
            }
        }

        return true;
    }

	return {
        createStep: createStep,
		getIssuancePolicies: getIssuancePolicies,
		getApprovalGroups: getApprovalGroups,
		getSigningCerts: getSigningCerts,
		getFilterResults: getFilterResults,
		getObjectTotalCount: getObjectTotalCount,
        getAllObjectsForTypes: getAllObjectsForTypes,
		getProfileExtensionSet: getProfileExtensionSet,
		getCertExtensionSet: getCertExtensionSet,
		getDNProfiles: getDNProfiles,
		getDNProfilesAsFormData: getDNProfilesAsFormData,
        getObjects: getObjects,
		validateCsr: validateCsr,
		clientValidateCsr: clientValidateCsr,
		getFormDataFromUploadedCsr: getFormDataFromUploadedCsr,
		getFirstInnerObj: getFirstInnerObj,
		getFirstInnerValue: getFirstInnerValue,
		getObjKeys: getObjKeys,
		keyTypeDefs: keyTypeDefs,
		keyTypeToString: keyTypeToString,
		keyTypeStringToFormParams: keyTypeStringToFormParams,
        ldapAuth: ldapAuth,
        objectFieldSchema: filterService.objectFieldSchema,
		determineInitialKeyTypeValue: determineInitialKeyTypeValue,
		addItemToExtension: addItemToExtension,
		removeItemFromExtension: removeItemFromExtension,
		sortExtOptions: sortExtOptions,
		removeDuplicateOptions: removeDuplicateOptions,
		addExtension: addExtension,
		removeExtension: removeExtension,
		isExtensionDisabled: isExtensionDisabled,
		semicolonsToCommas: fxAppStringService.semicolonsToCommas,
		removeWhitespace: fxAppStringService.removeWhitespace,
		strToCSV: fxAppStringService.strToCSV,
		capitalizeFirstLetter: fxAppStringService.capitalizeFirstLetter,
		dotsToUnderscores: fxAppStringService.dotsToUnderscores,
		underscoresToDots: fxAppStringService.underscoresToDots,
		spacesToUnderscores: fxAppStringService.spacesToUnderscores,
		hexToArrayBuffer: fxEncodeService.hexToArrayBuffer,
		downloadString: fxAppStringService.downloadString,
		ISOTimetoFXTime: fxAppStringService.ISOTimetoFXTime,
        hexEncode: fxEncodeService.hexEncode,
        hexDecode: fxEncodeService.hexDecode,
		curlyBraceStringToArray: fxAppStringService.curlyBraceStringToArray,
		isPEM: fxAppX509Service.isPEM,
		subjectParse: fxAppX509Service.subjectParse,
		subjectToString: fxAppX509Service.subjectToString,
		maskDNWithProfile: fxAppX509Service.maskDNWithProfile,
		getAllExtensions: fxAppX509Service.getAllExtensions,
		getV3ExtensionModes: fxAppX509Service.getV3ExtensionModes,
		translateV3ExtensionModeNameToEnum: fxAppX509Service.translateV3ExtensionModeNameToEnum,
		translateV3ExtensionModeEnumToName: fxAppX509Service.translateV3ExtensionModeEnumToName,
		createExtensionDescriptions: fxAppX509Service.createExtensionDescriptions,
		convertV3ExtensionDescriptionStringToArrayOfObjects: fxAppX509Service.convertV3ExtensionDescriptionStringToArrayOfObjects,
		getV3ExtensionNameFromOID: fxAppX509Service.getV3ExtensionNameFromOID,
		getV3ExtensionModeFromOID: fxAppX509Service.getV3ExtensionModeFromOID,
		convertV3ExtensionsStringToArrayOfObjects: fxAppX509Service.convertV3ExtensionsStringToArrayOfObjects,
		createV3ExtensionsString: fxAppX509Service.createV3ExtensionsString,
		updateExtensionValues: fxAppX509Service.updateExtensionValues,
		checkCustomOID: fxAppX509Service.checkCustomOID,
        removeDuplicates: removeDuplicates,
        slowPromise: slowPromise,
		updateASN1Preview: fxAppX509Service.updateASN1Preview,
        emailRegex: fxAppStringService.emailRegex,
        objectFalse: objectFalse,
	};
}]);
