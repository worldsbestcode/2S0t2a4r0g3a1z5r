/**
 * Provides common definitions for handling X.509 cert data
 *
 * @returns {object}    helper functions for fxAppX509Service
 */

var fxAppX509ServiceDefs = fxApp.factory('fxAppX509ServiceDefs',
	['$http', '$q', '$timeout', 'fxAppService', 'fxAppStringService',
	function($http, $q, $timeout, fxAppService, fxAppStringService) {

  // Moved to X509ServiceDefs.js
	return {
		getKnownDNProfile: Scaffolding.X509ServiceDefs.getKnownDNProfile,
		getHashTypes: Scaffolding.X509ServiceDefs.getHashTypes,
		getAuthorityInformationAccessTypes: Scaffolding.X509ServiceDefs.getAuthorityInformationAccessTypes,
		getCRLDistributionPointsTypes: Scaffolding.X509ServiceDefs.getCRLDistributionPointsTypes,
		getCertificatePolicies: Scaffolding.X509ServiceDefs.getCertificatePolicies,
		getCertificatePolicyQualifiers: Scaffolding.X509ServiceDefs.getCertificatePolicyQualifiers,
		getAllExtensions: Scaffolding.X509ServiceDefs.getAllExtensions,
		getV3ExtensionModes: Scaffolding.X509ServiceDefs.getV3ExtensionModes,
		getDirectoryNameTypes: Scaffolding.X509ServiceDefs.getDirectoryNameTypes,
		getSubjectAlternateNameTypes: Scaffolding.X509ServiceDefs.getSubjectAlternateNameTypes
	};
}]);
