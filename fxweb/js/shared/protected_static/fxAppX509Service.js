/**
 * Provides common functions for handling X.509 cert data
 *
 * @returns {object}    helper functions for fxAppViewService
 */

var fxAppX509Service = fxApp.factory('fxAppX509Service',
    ['$http', '$q', '$timeout', 'fxAppService', 'fxAppStringService', 'fxAppX509ServiceDefs', 'fxEncodeService',
    function($http, $q, $timeout, fxAppService, fxAppStringService, fxAppX509ServiceDefs, fxEncodeService) {

	/**
	 * Check if data is PEM or not
	 * @param {string} data The value to check
	 * @param {bool} isHex  If the header should be hex encoded before comparison
	 * @returns {bool} True if PEM false otherwise
	 */
	function isPEM (data, isHex) {
		var pemHeader = "-----BEGIN ";
		if (isHex) {
            pemHeader = fxEncodeService.hexEncode(pemHeader);
		}

		return data.substring(0, pemHeader.length) === pemHeader
	}

    /**
     * Pem encode a der encoded hex string
     * @param {string}  name - The name of the encoded type
     * @param {string}  hex - The string to encode
     * @returns {string}  The pem encoded value or an empty string on error
     */
    function pemEncode(name, hex) {
        var first = '-----BEGIN ' + name + '-----';
        var last = '-----END ' + name + '-----'
        return hex ? [first, hextob64nl(hex), last].join('\r\n') : '';
    }

	/**
	 * Converts a subject string into an object
	 * ex: "{2.5.4.6,19,5553}, ..."
	 *
	 * @param   {string}    subject - the CSV subject string
	 * @returns {object}    object representation of the subject
	 */
	function subjectParse(subject) {
		// split into DN fields
		var subjectArr = fxAppStringService.curlyBraceStringToArray(subject);
		var subjectObj = {};

		// process each DN field
		for (var i in subjectArr) {
			// split each DN field into OID, type, and value
			var field = subjectArr[i].split(',');
			field = {
				OID: 'OID_' + field[0].replace(/[.]/g, '_'),
				type: field[1],
				value: field[2]
			};

			// hex decode the value
            var decodedStr = fxEncodeService.hexDecode(field.value);
			field.value = decodedStr;

			// add to subjectObj
			subjectObj[field.OID] = {
				type: field.type,
				value: field.value
			};
		}

		return subjectObj;
	}

	/**
	 * Converts a subject object into a string
	 * ex: { "2.5.4.6": "type": "19", "value": "5553" }
	 *
	 * @param   {object}    subject - object representation of the subject
	 * @returns {string}    subject string or whatever was passed to the function
	 */
	function subjectToString(subjectObj) {
		if (typeof subjectObj === "object") {
			var subjectArr = [];
			for (var OID in subjectObj) {
				// convert OID back to string format
				var OIDStr = OID.substring(4, OID.length).replace(/[_]/g, '.');

				// hex encode the value
                var encodedStr = fxEncodeService.hexEncode(subjectObj[OID].value);

				// append to the returned array
				var OIDFormatted = '{' + OIDStr + ',' + subjectObj[OID].type +
					',' + encodedStr.toUpperCase() + '}';

				subjectArr.push(OIDFormatted);
			}
			return subjectArr.join();
		}
		else {
			return subjectObj;
		}
	}

	/**
	 * Given a CSR, make sure that the DN only uses the
	 * OIDs defined in the profile
	 *
	 * @param   {object}     csr - certificate signing request
	 */
	function maskDNWithProfile(csr) {
		if (csr) {
			// Name of the selected DN profile
			var name = csr.selectedDNProfile.name;

			// If there is no profile, just use the subject
			if (name === 'None') {
				return csr.subject;
			}

			// Use the selected DN profile
			else {
				// The selected DN profile
				var result = csr.selectedDNProfile.extensions;

				// Copy values into the profile
				for (var OID in result) {
					result[OID].value = csr.subject[OID] ? csr.subject[OID].value : '';
				}

				return result;
			}
		}
	}

	/**
	 * Translate the mode name into its enum value
	 *
	 * @param   {string}     modeName - the extension mode display name
	 * @returns {integer}    the extension mode
	 */
	function translateV3ExtensionModeNameToEnum(modeName) {
		var extensionModes = fxAppX509ServiceDefs.getV3ExtensionModes();
		var result = extensionModes[modeName];

		return result ? result : extensionModes['None'];
	}

	function translateV3ExtensionModeEnumToName(modeEnum) {
		var extensionModes = fxAppX509ServiceDefs.getV3ExtensionModes();
		var result = Object.keys(extensionModes).filter(function(modeName) {
			return String(extensionModes[modeName]) === modeEnum;
		});

		return result.length > 0 ? result[0] : 'None';
	}

	/**
	 * Generate the extension description string for a cert request
	 *
	 * @param   {array}     extensions - an array of extension objects
	 * @returns {string}    the description string
	 */
	function createExtensionDescriptions(extensions) {
		return extensions.map(function(extension) {
			// Skip incomplete extensions
			if (extension.oid && extension.mode) {
				// Generate the description string
				return '{' +
					fxAppStringService.underscoresToDots(extension.oid) + ',' +
					translateV3ExtensionModeNameToEnum(extension.mode) + '}';
			}
			else {
				return;
			}
		}).filter(function(description) {
			// Remove skipped extension descriptions from the array
			return description !== undefined;
		}).join(',');
	}

	/**
	 * Deserialize the extension description string
	 *
	 * @param   {string}    v3ExtensionDesc - the extension description
	 * @returns {object}    the oid and mode
	 */
	function convertV3ExtensionDescriptionStringToArrayOfObjects(v3ExtensionDesc) {
		var descriptionStrings = fxAppStringService.curlyBraceStringToArray(v3ExtensionDesc);

		return descriptionStrings.map(function(descriptionString) {
			var description = descriptionString.split(',');

			return {
				oid: description[0],
				mode: description[1]
			};
		});
	}

	/**
	 * Get the extension name by OID
	 *
	 * @param   {string}    oid - the extension OID
	 * @returns {string}    extension name
	 */
	function getV3ExtensionNameFromOID(oid) {
		var result = fxAppX509ServiceDefs.getAllExtensions().filter(function(extension) {
			return extension.oid === oid;
		});

		return result.length > 0 ? result[0].name : oid;
	}

	/**
	 * Check whether the extension uses the default form
	 * (default form allows the user to paste in ASN.1 hex)
	 *
	 * @param   {string}        oid - the extension OID
	 * @returns {boolean}    whether to use the default form
	 */
	function getUseDefaultFormFromOID(oid) {
		var result = fxAppX509ServiceDefs.getAllExtensions().filter(function(extension) {
			return extension.oid === oid;
		});

		return result.length > 0 ? result[0].useDefaultForm : true;
	}

	/**
	 * Get the custom form data of an extension
	 *
	 * @param   {string}       oid - the extension OID
	 * @param   {string}    v3ExtensionDesc - the extension descriptions
	 * @returns {object}    the custom form data for a given extension
	 */
	function getCustomFormDataFromOID(oid) {
		var result = fxAppX509ServiceDefs.getAllExtensions().filter(function(extension) {
			return extension.oid === oid && extension.customFormData;
		});

		return result.length > 0 ? result[0].customFormData : undefined;
	}

	/**
	 * Get the default mode of the extension
	 *
	 * @param   {string}       oid - the extension OID
	 * @param   {string}    v3ExtensionDesc - the extension descriptions
	 */
	function getV3ExtensionModeFromOID(oid, v3ExtensionDesc) {
		var descriptions = convertV3ExtensionDescriptionStringToArrayOfObjects(v3ExtensionDesc);
		var result = descriptions.filter(function(description) {
			return fxAppStringService.dotsToUnderscores(description.oid) === oid;
		});

		if (result.length > 0) {
			return translateV3ExtensionModeEnumToName(result[0].mode);
		}
		else {
			return 'None';
		}
	}

	/**
	 * Get the type from the TLV string
	 *
	 * @param   {string}    tlvStr - the ASN.1 TLV string
	 */
	function getTypeFromTLV(tlvStr) {
		return tlvStr.slice(0,2).toLowerCase();
	}

	/**
	 * Find the offset in the ASN.1 where the IA5String with the URI tag begins
	 * (this is needed because "ASN1HEX.getPosArrayOfChildren_AtObj" does not
	 * find the indices of child items in a SEQUENCE if they have tags)
	 *
	 * @param   {string}    str - the ASN.1 string
	 */
	function findIA5StringWithURITag(str) {
		// Assume 2 chars per byte
		if (str.length % 2 !== 0 || str.length < 1) {
			return str.length;
		}

		// Find "0x86"
		for (var i = 0; i < str.length; i += 2) {
			if (str[i] + str[i+1] === '86') {
				return i;
			}
		}

		return str.length;
	}

	/**
	 * Get the type from the TLV string
	 *
	 * @param   {string}    tlvStr - the ASN.1 TLV string
	 * @returns {string}    the name of the type
	 */
	function getSubjectAlternateNameType(tlvStr) {
		return fxAppX509ServiceDefs.getSubjectAlternateNameTypes().filter(function(type) {
			return getTypeFromTLV(tlvStr) === type.tag;
		})[0];
	}

	/**
	 * Decode the extension values into form data
	 *
	 * @param   {object}    extension - the extension being updated
	 */
	function customFormDataFromExtensionValues(extension) {
		var oid = fxAppStringService.dotsToUnderscores(extension[0]);
		var value = fxAppStringService.dotsToUnderscores(extension[1]);
		var customFormData = getCustomFormDataFromOID(oid);

		// Authority Key Identifier
		if (oid === '2_5_29_35') {
			customFormData.options.map(function(option) {
				if (option.value === value) {
					customFormData.selected = option;
				}
			});
		}

		// Subject Key Identifier
		else if (oid === '2_5_29_14') {
			customFormData.options.map(function(option) {
				if (option.value === value) {
					customFormData.selected = option;
				}
			});
		}

		// Subject Alternate Name
		else if (oid === '2_5_29_17') {
			customFormData.names = ASN1HEX.getPosArrayOfChildren_AtObj(
				value,
				0
			).reduce(function(result, index) {
				var type = getSubjectAlternateNameType(ASN1HEX.getHexOfTLV_AtObj(value, index));

				if (type) {
					switch(type.name) {
						case 'Email':
						case 'DNS Name':
						case 'URI':
							type.value = fxEncodeService.hexDecode(
								ASN1HEX.getHexOfV_AtObj(value, index)
							);
							break;
						case 'IP Address':
							type.value = fxEncodeService.hexDecodeOctet(
								ASN1HEX.getHexOfV_AtObj(value, index)
							).join('.');
							break;
						case 'Other Name':
							var otherNameHex = ASN1HEX.getHexOfTLV_AtObj(value, index);
							var otherNameIndices = ASN1HEX.getPosArrayOfChildren_AtObj(otherNameHex, 0);
							type.oid = ASN1HEX.hextooidstr(ASN1HEX.getHexOfV_AtObj(otherNameHex, otherNameIndices[0]));
							type.value = ASN1HEX.getHexOfV_AtObj(otherNameHex, otherNameIndices[1]);
							type.parsedPreview = ASN1HEX.dump(type.value);
							type.parseFailed = type.parsedPreview.length > 0;
							break;
						case 'Directory Name':
							var directoryNameHex = ASN1HEX.getHexOfV_AtObj(value, index);
							var directoryNameIndices = ASN1HEX.getPosArrayOfChildren_AtObj(directoryNameHex, 0);
							var directoryNameTypes = fxAppX509ServiceDefs.getDirectoryNameTypes();

							type.names = directoryNameIndices.map(function(index) {
								var directoryNameItemHex = ASN1HEX.getHexOfV_AtObj(directoryNameHex, index);
								var directoryNameItemIndices = ASN1HEX.getPosArrayOfChildren_AtObj(directoryNameItemHex, 0);

								// Find type by OID
								var directoryNameItemOID = fxAppStringService.dotsToUnderscores(
									ASN1HEX.hextooidstr(ASN1HEX.getHexOfV_AtObj(directoryNameItemHex, directoryNameItemIndices[0]))
								);
								var directoryNameType = directoryNameTypes.filter(function(type) {
									return type.oid === directoryNameItemOID;
								})[0] || directoryNameTypes.filter(function(type) {
									return type.name === 'Custom';
								})[0];

								// Populate directoryNameType
								directoryNameType.oid = fxAppStringService.underscoresToDots(directoryNameItemOID);
								directoryNameType.value = fxEncodeService.hexDecode(
									ASN1HEX.getHexOfV_AtObj(directoryNameItemHex, directoryNameItemIndices[1])
								);

								return directoryNameType;
							});
							break;
						default:
							break;
					}

					result.push(type);
				}

				return result;
			}, []);
		}

		// Key Usage
		else if (oid === '2_5_29_15') {
			// Convert two bytes from hex to binary and least-significant digit is bitField[0]
			var bitField = fxAppStringService.changeBase(ASN1HEX.getHexOfV_AtObj(value, 0), 16, 2, 16, true);

			customFormData.options.map(function(option) {
				if (option.name === 'Encipher Only') {
					option.value = parseInt(bitField[0]) > 0;
				}
				else if (option.name === 'CRL Sign') {
					option.value = parseInt(bitField[1]) > 0;
				}
				else if (option.name === 'Certificate Sign') {
					option.value = parseInt(bitField[2]) > 0;
				}
				else if (option.name === 'Key Agreement') {
					option.value = parseInt(bitField[3]) > 0;
				}
				else if (option.name === 'Data Encipherment') {
					option.value = parseInt(bitField[4]) > 0;
				}
				else if (option.name === 'Key Encipherment') {
					option.value = parseInt(bitField[5]) > 0;
				}
				else if (option.name === 'Non Repudiation') {
					option.value = parseInt(bitField[6]) > 0;
				}
				else if (option.name === 'Digital Signature') {
					option.value = parseInt(bitField[7]) > 0;
				}
				else if (option.name === 'Decipher Only') {
					option.value = parseInt(bitField[15]) > 0;
				}
			});
		}

		// Extended Key Usage
		else if (oid === '2_5_29_37') {
			// Get OIDs
			var enabledOIDs = ASN1HEX.getPosArrayOfChildren_AtObj(
				value,
				0
			).map(function(index) {
				return fxAppStringService.dotsToUnderscores(
					ASN1HEX.hextooidstr(ASN1HEX.getHexOfV_AtObj(value, index))
				);
			});

			// Set the form data
			customFormData.options.map(function(option) {
				option.value = enabledOIDs.filter(function(oid) {
					return oid === option.oid;
				}).length > 0;
			});
		}

		// Authority Information Access
		else if (oid === '1_3_6_1_5_5_7_1_1') {
			// Get hex of each option
			ASN1HEX.getPosArrayOfChildren_AtObj(value, 0).map(function(index) {
				return ASN1HEX.getHexOfV_AtObj(value, index);

			// Get OID and value of each option
			}).map(function(option) {
				var oid = fxAppStringService.dotsToUnderscores(
					ASN1HEX.hextooidstr(ASN1HEX.getHexOfV_AtObj(option, 0))
				);

                var value = fxEncodeService.hexDecode(
					ASN1HEX.getHexOfV_AtObj(option, findIA5StringWithURITag(option))
				);

				// Populate form data
				customFormData.items.push({
					value: value,
					type: customFormData.types.filter(function(type) {
						return type.oid === oid;
					})[0]
				});
			});
		}

		// CRL Distribution Points
		else if (oid === '2_5_29_31') {
			// Add items to form data
			ASN1HEX.getPosArrayOfChildren_AtObj(value, 0).map(function(index) {
				// Get item value
				var item = ASN1HEX.getHexOfV_AtObj(value, index);
                var itemValue = fxEncodeService.hexDecode(
					ASN1HEX.getHexOfV_AtObj(item, findIA5StringWithURITag(item))
				);

				// Add item
				var newItem = angular.copy(customFormData.defaultItem);
				newItem.value = itemValue;
				customFormData.items.push(newItem);
			});
		}

		// Basic Constraints
		else if (oid === '2_5_29_19') {
			// Get values
			var indices = ASN1HEX.getPosArrayOfChildren_AtObj(value, 0);
            var caEnabledHex = ASN1HEX.getHexOfV_AtObj(value, indices[0]);
            var caEnabled = parseInt(caEnabledHex, 16) > 0;
			var pathLengthHex = ASN1HEX.getHexOfV_AtObj(value, indices[1]);
			var pathLengthConstraint = pathLengthHex.length > 0;
			var pathLength = parseInt(pathLengthHex, 16);

			// Set form data
			customFormData.ca = caEnabled;
			customFormData.pathLengthConstraint = pathLengthConstraint;
			customFormData.pathLengthValue = pathLengthConstraint ? pathLength : 0;
		}

		// Certificate Policies
		else if (oid === '2_5_29_32') {
			ASN1HEX.getPosArrayOfChildren_AtObj(value, 0).map(function(policyIndex) {
				var policyHex = ASN1HEX.getHexOfTLV_AtObj(value, policyIndex);
				var policyIndices = ASN1HEX.getPosArrayOfChildren_AtObj(policyHex, 0);

				// Policy
				var policyOID = ASN1HEX.hextooidstr(ASN1HEX.getHexOfV_AtObj(policyHex, policyIndices[0]));
				var newPolicy = angular.copy(customFormData.policyTypes.filter(function(policyType) {
					return policyType.oid === fxAppStringService.dotsToUnderscores(policyOID);
				})[0] || customFormData.policyTypes.filter(function(policyType) {
					return policyType.name === "Custom";
				})[0]);

				// Policy OID must be set when it's a custom policy
				if (newPolicy.oid.length < 1) {
					newPolicy.oid = fxAppStringService.dotsToUnderscores(policyOID);
				}

				// Qualifiers
				var qualifiersHex = ASN1HEX.getHexOfTLV_AtObj(policyHex, policyIndices[1]);
				ASN1HEX.getPosArrayOfChildren_AtObj(qualifiersHex, 0).map(function(qualifierIndex) {
					var qualifierHex = ASN1HEX.getHexOfTLV_AtObj(qualifiersHex, qualifierIndex);
					var qualifierIndices = ASN1HEX.getPosArrayOfChildren_AtObj(qualifierHex, 0);

					// Check that qualifier is present
					if (qualifierHex.length) {
						// Qualifier
						var qualifierOID = ASN1HEX.hextooidstr(ASN1HEX.getHexOfV_AtObj(qualifierHex, qualifierIndices[0]));
						var newQualifier = angular.copy(customFormData.qualifierTypes.filter(function(qualifierType) {
							return qualifierType.oid === fxAppStringService.dotsToUnderscores(qualifierOID);
						})[0] || customFormData.qualifierTypes.filter(function(qualifierType) {
							return qualifierType.name === "Custom";
						})[0]);

						// CPS URI
						if (newQualifier.oid === '1_3_6_1_5_5_7_2_1') {
                            newQualifier.uri = fxEncodeService.hexDecode(
								ASN1HEX.getHexOfV_AtObj(qualifierHex, qualifierIndices[1])
							);
						}

						// User Notice
						else if (newQualifier.oid === '1_3_6_1_5_5_7_2_2') {
							var formHex = ASN1HEX.getHexOfTLV_AtObj(qualifierHex, qualifierIndices[1]);
							var formIndices = ASN1HEX.getPosArrayOfChildren_AtObj(formHex, 0);

							// Explicit text
                            newQualifier.explicitText = fxEncodeService.hexDecode(ASN1HEX.getHexOfV_AtObj(formHex, formIndices[1]));

							// Use explicit text
							newQualifier.useExplicitText = newQualifier.explicitText.length > 0;

							var noticeReferenceHex = ASN1HEX.getHexOfTLV_AtObj(formHex, formIndices[0]);
							var noticeReferenceIndices = ASN1HEX.getPosArrayOfChildren_AtObj(noticeReferenceHex, 0);

							// Organization
                            newQualifier.noticeReference.organization = fxEncodeService.hexDecode(
								ASN1HEX.getHexOfV_AtObj(noticeReferenceHex, noticeReferenceIndices[0])
							);

							var noticeNumbersSequenceHex = ASN1HEX.getHexOfTLV_AtObj(noticeReferenceHex, noticeReferenceIndices[1]);
							var noticeNumbersSequenceIndices = ASN1HEX.getPosArrayOfChildren_AtObj(noticeNumbersSequenceHex, 0);

							// Notice numbers
							newQualifier.noticeReference.noticeNumbers = parseInt(
								ASN1HEX.getHexOfV_AtObj(noticeNumbersSequenceHex, noticeNumbersSequenceIndices[0]),
								16
							).toString();

							// Use notice reference
							newQualifier.useNoticeReference = newQualifier.noticeReference.organization.length > 0 ||
								newQualifier.noticeReference.noticeNumbers.length > 0;
						}

						// Custom
						else {
							newQualifier.oid = qualifierOID;
							newQualifier.value = ASN1HEX.getHexOfV_AtObj(qualifierHex, qualifierIndices[1]);
						}

						newPolicy.qualifiers.push(newQualifier);
					}
				});

				customFormData.policies.push(newPolicy);
			});
		}

		return customFormData;
	}

	/**
	 * Deserialize the extensions from curly-brace string format
	 *
	 * @param   {object}    v3Extensions - the extensions
	 * @param   {object}    v3ExtensionDesc - the extension descriptions
	 */
	function convertV3ExtensionsStringToArrayOfObjects(v3Extensions, v3ExtensionDesc) {
		if (v3Extensions.length) {
			var extensionStrings = fxAppStringService.curlyBraceStringToArray(v3Extensions);

			return extensionStrings.map(function(extensionString) {
				var extension = extensionString.split(',');
				var oid = fxAppStringService.dotsToUnderscores(extension[0]);

				return {
					name: getV3ExtensionNameFromOID(oid),
					oid: oid,
					critical: (extension[2] === "1" ? true : false),
					mode: getV3ExtensionModeFromOID(oid, v3ExtensionDesc),
					value: extension[1],
					useDefaultForm: getUseDefaultFormFromOID(oid),
					customFormData: customFormDataFromExtensionValues(extension)
				};
			});
		}
		else {
			return [];
		}
	}

	/**
	 * Serialize the extensions into curly-brace string format
	 *
	 * @param   {object}    v3Extensions - the extensions
	 */
	function createV3ExtensionsString(v3Extensions) {
		return v3Extensions.map(function(extension) {
			// Skip incomplete extensions
			if (extension.oid && typeof extension.critical === 'boolean') {
				// Generate the extension string
				return '{' +
					fxAppStringService.underscoresToDots(extension.oid) + ',' +
					(extension.value ? extension.value : '') + ',' +
					(extension.critical ? '1' : '0') + '}';
			}
			else {
				return;
			}
		}).filter(function(extensionString) {
			return extensionString !== undefined;
		}).join(',');
	}

	/**
	 * Encode the extension values from the form data
	 *
	 * @param   {object}    extension - the extension being updated
	 */
	function updateExtensionValues(extensions) {
		extensions.map(function(extension) {
			// Authority Key Identifier
			if (extension.oid === '2_5_29_35') {
				extension.value = extension.customFormData.selected.value;
			}

			// Subject Key Identifier
			else if (extension.oid === '2_5_29_14') {
				extension.value = extension.customFormData.selected.value;
			}

			// Subject Alternate Name
			else if (extension.oid === '2_5_29_17') {
				// Must have names defined before trying to parse
				if (extension.customFormData.names) {
					extension.value = new KJUR.asn1.DERSequence({
						array: extension.customFormData.names.map(function(item) {
							switch(item.name) {
								case 'Email':
								case 'DNS Name':
								case 'URI':
									return new KJUR.asn1.DERTaggedObject({
										tag: item.tag,
										explicit: false,
										obj: new KJUR.asn1.DERUTF8String({
											str: item.value
										})
									});
									break;
								case 'IP Address':
									return new KJUR.asn1.DERTaggedObject({
										tag: item.tag,
										explicit: false,
										obj: new KJUR.asn1.DEROctetString({
											hex: fxEncodeService.hexEncodeOctet(item.value.split('.'))
										})
									});
									break;
								case 'Other Name':
									return new KJUR.asn1.DERTaggedObject({
										tag: item.tag,
										explicit: false,
										obj: new KJUR.asn1.DERSequence({
											array: [
												new KJUR.asn1.DERObjectIdentifier({
													oid: item.oid
												}),
												new KJUR.asn1.DERTaggedObject({
													tag: item.tag,
													explicit: false,
													obj: new KJUR.asn1.DEROctetString({
														hex: item.value
													})
												})
											]
										})
									});
									break;
								case 'Directory Name':
									return new KJUR.asn1.DERTaggedObject({
										tag: item.tag,
										explicit: false,
										obj: new KJUR.asn1.DERSequence({
											array: [
												new KJUR.asn1.DERSequence({
													array: item.names.map(function(name) {
														return new KJUR.asn1.DERSet({
															array: [
																new KJUR.asn1.DERSequence({
																	array: [
																		new KJUR.asn1.DERObjectIdentifier({
																			oid: name.oid
																		}),
																		new KJUR.asn1.DERUTF8String({
																			str: name.value
																		})
																	]
																})
															]
														});
													})
												})
											]
										})
									});
									break;
								default:
									break;
							}
						})
					}).getEncodedHex();
				}
			}

			// Key Usage
			else if (extension.oid === '2_5_29_15') {
				extension.value = new KJUR.asn1.DERBitString({
					array: extension.customFormData.options.map(function(option) {
						return option.value;
					})
				}).getEncodedHex();
			}

			// Extended Key Usage
			else if (extension.oid === '2_5_29_37') {
				extension.value = new KJUR.asn1.DERSequence({
					array: extension.customFormData.options.map(function(option) {
						if (option.value) {
							return new KJUR.asn1.DERObjectIdentifier({
								oid: fxAppStringService.underscoresToDots(option.oid)
							});
						}
					}).filter(function(option) {
						return typeof option !== 'undefined';
					})
				}).getEncodedHex();
			}

			// Authority Information Access
			else if (extension.oid === '1_3_6_1_5_5_7_1_1') {
				// Generate extension hex
				var AuthorityInformationAccessHex = new KJUR.asn1.x509.AuthorityInfoAccess({
                    array: extension.customFormData.items.filter(function(item) {
                        return item.value !== "";
                    }).map(function(item) {
						return {
							accessMethod: {
								oid: fxAppStringService.underscoresToDots(item.type.oid)
							},
							accessLocation: {
								uri: item.value
							}
						};
					})
				}).getEncodedHex();

				// Set only the value from the [OID, value] array
				extension.value = ASN1HEX.getHexOfV_AtObj(
					AuthorityInformationAccessHex,
					ASN1HEX.getPosArrayOfChildren_AtObj(AuthorityInformationAccessHex, 0)[1]
				);
			}

			// CRL Distribution Points
			else if (extension.oid === '2_5_29_31') {
				// Generate extension hex
				var CRLDistributionPointsHex = new KJUR.asn1.x509.CRLDistributionPoints({
					critical: true,
					array: extension.customFormData.items.map(function(item) {
						return new KJUR.asn1.x509.DistributionPoint({
							dpobj: new KJUR.asn1.x509.DistributionPointName(
								new KJUR.asn1.x509.GeneralNames([{
									uri: item.value
								}])
							)
						});
					})
				}).getEncodedHex();

				// Set only the value from the [OID, critical, value] array
				extension.value = ASN1HEX.getHexOfV_AtObj(
					CRLDistributionPointsHex,
					ASN1HEX.getPosArrayOfChildren_AtObj(CRLDistributionPointsHex, 0)[2]
				);
			}

			// Basic Constraints
			else if (extension.oid === '2_5_29_19') {
				// Build the ASN.1 sequence
				var sequence = [];
                if (extension.customFormData.ca) {
                    sequence.push(new KJUR.asn1.DERBoolean(extension.customFormData.ca));
                    if (extension.customFormData.pathLengthValue > 0) {
                        sequence.push(new KJUR.asn1.DERInteger(extension.customFormData.pathLengthValue));
                    }
				}

				// Set the hex value
				extension.value = new KJUR.asn1.DERSequence({
					array: sequence
				}).getEncodedHex();
			}

			// Certificate Policies
			else if (extension.oid === '2_5_29_32') {
				var sequence = new KJUR.asn1.DERSequence({
					array: extension.customFormData.policies.map(function(policy) {
						// Policies
						return new KJUR.asn1.DERSequence({
							array: [
								new KJUR.asn1.DERObjectIdentifier({
									oid: fxAppStringService.underscoresToDots(policy.oid)
								}),
								new KJUR.asn1.DERSequence({
									// Qualifiers
									array: policy.qualifiers.map(function(qualifier) {
										var qualifierData = {};
										// CPS URI
										if (qualifier.oid === '1_3_6_1_5_5_7_2_1') {
											qualifierData = new KJUR.asn1.DERIA5String({
												str: qualifier.uri
											});
										}
										// User Notice
										else if (qualifier.oid === '1_3_6_1_5_5_7_2_2') {
											qualifierData = new KJUR.asn1.DERSequence({
												array: [
													new KJUR.asn1.DERSequence({
														array: [
															new KJUR.asn1.DERUTF8String({
																str: qualifier.noticeReference.organization
															}),
															new KJUR.asn1.DERInteger({
																int: parseInt(qualifier.noticeReference.noticeNumbers)
															})
														]
													}),
													new KJUR.asn1.DERUTF8String({
														str: qualifier.explicitText
													})
												]
											});
										}
										// Custom
										else {
											if (qualifier.value.length > 0) {
												qualifierData = new KJUR.asn1.DERUTF8String({
													str: qualifier.value
												});
											}
										}
										// Qualifier
										return new KJUR.asn1.DERSequence({
											array: qualifier.oid ? [
												new KJUR.asn1.DERObjectIdentifier({
													oid: fxAppStringService.underscoresToDots(qualifier.oid)
												}),
												qualifierData
											] : []
										})
									})
								})
							]
						});
					})
				});

				try {
					extension.value = sequence.getEncodedHex();
				}
				catch(e) {
					// Ignore parsing errors with this particular extension.
					// "getEncodedHex" becomes undefined when the constructors
					// are called with incomplete or incorrect extension form
					// data. This is called on every extension form data value
					// or reference change, including when the user is typing.
				}
			}
		});
	};

	/**
	 * Check that an OID doesn't collide with any other extensions
	 *
	 * @param   {string}     oid - An OID
	 * @param   {array}      selectedExtensions - already selected extensions
	 * @returns {boolean}    whether the OID collides
	 */
	function checkOIDCollision(oid, selectedExtensions) {
		// Check against pre-defined extensions
		var collisionExtensions = fxAppX509ServiceDefs.getAllExtensions().filter(function(extension) {
			if (extension.oid !== '') {
				return oid === fxAppStringService.underscoresToDots(extension.oid);
			}
		}).length > 0;

		// Check against the other custom extensions
		var collisionCustomExtensions = selectedExtensions.filter(function(extension) {
			if (extension.oid !== '') {
				return extension.name === 'Custom' && oid === extension.oid;
			}
		}).length > 1;

		return collisionExtensions || collisionCustomExtensions;
	}

	/**
	 * Provides a callback to perform additional checking onblur of input mask
	 *
	 * @param   {object}     extension - the extension being edited
	 * @param   {integer}    $index - ng-repeat index of the selected extension
	 * @param   {object}     formdata - the form data
	 * @returns {function}   onblur callback that gets passed to fx-input-mask
	 */
	function checkCustomOID(extension, $index, formdata) {
		return function(oid) {
			// Check against predefined and already selected extensions
			if (checkOIDCollision(oid, formdata.v3Extensions)) {
				// Reset the input
				extension.oid = '';

				// Give user feedback
				$('div#custom-oid-' + $index).notify(
					'Duplicate OID',
					{ position: 'bottom center' }
				);
			}
		};
	}

	/**
	 * Update the ASN.1 preview textarea for extensions that need it
	 *
	 * @param   {object}    extension - the extension being updated
	 */
	function updateASN1Preview(extension) {
		// Validate
		extension.customFormData.parseFailed = !ASN1HEX.isASN1HEX(extension.value);
		if (!extension.customFormData.parseFailed) {
			extension.customFormData.parsedPreview = ASN1HEX.dump(extension.value);
		}
		else {
			extension.customFormData.parsedPreview = '';
		}
	}

	return {
		isPEM: isPEM,
        pemEncode: pemEncode,
		subjectParse: subjectParse,
		subjectToString: subjectToString,
		getAllExtensions: fxAppX509ServiceDefs.getAllExtensions,
		getV3ExtensionModes: fxAppX509ServiceDefs.getV3ExtensionModes,
		getKnownDNProfile: fxAppX509ServiceDefs.getKnownDNProfile,
		maskDNWithProfile: maskDNWithProfile,
		translateV3ExtensionModeNameToEnum: translateV3ExtensionModeNameToEnum,
		translateV3ExtensionModeEnumToName: translateV3ExtensionModeEnumToName,
		createExtensionDescriptions: createExtensionDescriptions,
		convertV3ExtensionDescriptionStringToArrayOfObjects: convertV3ExtensionDescriptionStringToArrayOfObjects,
		getV3ExtensionNameFromOID: getV3ExtensionNameFromOID,
		getUseDefaultFormFromOID: getUseDefaultFormFromOID,
		getV3ExtensionModeFromOID: getV3ExtensionModeFromOID,
		convertV3ExtensionsStringToArrayOfObjects: convertV3ExtensionsStringToArrayOfObjects,
		createV3ExtensionsString: createV3ExtensionsString,
		updateExtensionValues: updateExtensionValues,
		checkOIDCollision: checkOIDCollision,
		checkCustomOID: checkCustomOID,
		updateASN1Preview: updateASN1Preview
	};
}]);
