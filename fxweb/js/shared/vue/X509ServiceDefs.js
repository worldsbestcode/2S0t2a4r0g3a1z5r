/**
 * Provides common definitions for handling X.509 cert data
 *
 * @returns {object}    helper functions for fxAppX509Service
 */

/**
 * Retreive known DN profile presets by name
 *
 * @param   {string}    name - DN profile preset name
 */
function getKnownDNProfile (name) {
  // Default profiles
  var UTF8StringType = 12;
  var profiles = {
    'None': [
      '2_5_4_15',
      '2_5_4_3',
      '2_5_4_6',
      '2_5_4_46',
      '0_9_2342_19200300_100_1_25',
      '1_2_840_113549_1_9_1',
      '2_5_4_44',
      '2_5_4_42',
      '2_5_4_43',
      '1_3_6_1_4_1_311_60_2_1_3',
      '1_3_6_1_4_1_311_60_2_1_2',
      '2_5_4_7',
      '2_5_4_41',
      '2_5_4_10',
      '2_5_4_11',
      '2_5_4_17',
      '2_5_4_65',
      '2_5_4_5',
      '2_5_4_8',
      '2_5_4_9',
      '2_5_4_4',
      '2_5_4_12',
      '2_5_4_45'
    ],
    'Classic': [
      '2_5_4_6',
      '2_5_4_8',
      '2_5_4_7',
      '2_5_4_10',
      '2_5_4_11',
      '2_5_4_12',
      '2_5_4_3',
      '1_2_840_113549_1_9_1',
      '2_5_4_65'
    ]
  };

  // The profile requested
  var profile = profiles[name];

  // Resulting form data
  var result = {};

  // Build the form data from the profile OIDs
  if (profile) {
    profile.map(function (oid) {
      result['OID_' + oid] = {
        type: UTF8StringType,
        value: ''
      };
    });
  }

  return result;
}

/**
 * Get the hash type names
 *
 * @returns {array}    array of objects
 */
function getHashTypes () {
  return [
    {
      displayName: 'MD5',
      value: 'MD5'
    }, {
      displayName: 'RIPEMD-160',
      value: 'RIPEMD'
    }, {
      displayName: 'SHA-1',
      value: 'SHA1'
    }, {
      displayName: 'SHA-224',
      value: 'SHA224'
    }, {
      displayName: 'SHA-256',
      value: 'SHA256'
    }, {
      displayName: 'SHA-384',
      value: 'SHA384'
    }, {
      displayName: 'SHA-512',
      value: 'SHA512'
    }
  ];
}

/**
 * Get the types for the Authority Information Access extension
 *
 * @returns {array}    array of objects
 */
function getAuthorityInformationAccessTypes () {
  return [
    {
      name: 'HTTP',
      oid: '1_3_6_1_5_5_7_48_2'
    }, {
      name: 'LDAP',
      oid: '1_3_6_1_5_5_7_48_2'
    }, {
      name: 'OCSP',
      oid: '1_3_6_1_5_5_7_48_1'
    }
  ];
}

/**
 * Get the types for the CRL Distribution Points extension
 *
 * @returns {array}    array of objects
 */
function getCRLDistributionPointsTypes () {
  return [
    'HTTP',
    'LDAP'
  ];
}

/**
 * Get the certificate policies for the Certificate Policies extension
 *
 * @returns {array}    array of objects
 */
function getCertificatePolicies () {
  return [
    {
      name: 'Any Policy',
      oid: '2_5_29_32_0',
      qualifiers: []
    }, {
      name: 'Baseline Requirements',
      oid: '2_23_140_1_2',
      qualifiers: []
    }, {
      name: 'Domain Validated',
      oid: '2_23_140_1_2_1',
      qualifiers: []
    }, {
      name: 'Extended Validation',
      oid: '2_23_140_1_1',
      qualifiers: []
    }, {
      name: 'FPKI Common Authentication',
      oid: '2_16_840_1_101_3_2_1_3_13',
      qualifiers: []
    }, {
      name: 'FPKI Common Card Authentication',
      oid: '2_16_840_1_101_3_2_1_3_17',
      qualifiers: []
    }, {
      name: 'FPKI Common Devices',
      oid: '2_16_840_1_101_3_2_1_3_8',
      qualifiers: []
    }, {
      name: 'FPKI Common Devices Hardware',
      oid: '2_16_840_1_101_3_2_1_3_36',
      qualifiers: []
    }, {
      name: 'FPKI Common Hardware',
      oid: '2_16_840_1_101_3_2_1_3_7',
      qualifiers: []
    }, {
      name: 'FPKI Common High',
      oid: '2_16_840_1_101_3_2_1_3_16',
      qualifiers: []
    }, {
      name: 'FPKI Common PIV Authentication',
      oid: '2_16_840_1_101_3_2_1_3_40',
      qualifiers: []
    }, {
      name: 'FPKI Common PIV Content Signing',
      oid: '2_16_840_1_101_3_2_1_3_39',
      qualifiers: []
    }, {
      name: 'FPKI Common PIV Hardware Authentication',
      oid: '2_16_840_1_101_3_2_1_3_41',
      qualifiers: []
    }, {
      name: 'FPKI Common Policy',
      oid: '2_16_840_1_101_3_2_1_3_6',
      qualifiers: []
    }, {
      name: 'FPKI Common Trusted Server Authentication',
      oid: '2_16_840_1_101_3_2_1_3_42',
      qualifiers: []
    }, {
      name: 'Individual Validated',
      oid: '2_23_140_1_2_3',
      qualifiers: []
    }, {
      name: 'Organization Validated',
      oid: '2_23_140_1_2_2',
      qualifiers: []
    }, {
      name: 'Custom',
      oid: '',
      qualifiers: []
    }
  ];
}

/**
 * Get the qualifiers for the Certificate Policy extension
 *
 * @returns {array}    array of objects
 */
function getCertificatePolicyQualifiers () {
  return [
    {
      name: 'User Notice',
      oid: '1_3_6_1_5_5_7_2_2',
      useExplicitText: false,
      explicitText: '',
      useNoticeReference: false,
      noticeReference: {
        organization: '',
        noticeNumbers: ''
      }
    }, {
      name: 'CPS URI',
      oid: '1_3_6_1_5_5_7_2_1',
      uri: ''
    }, {
      name: 'Custom',
      oid: '',
      value: ''
    }
  ];
}

/**
 * Get the name types for the Directory Name type of Subject Alternate Name
 *
 * @returns {array}    array of objects
 */
function getDirectoryNameTypes () {
  return [
    {
      name: 'Custom',
      oid: '',
      value: ''
    }, {
      name: 'Business Category',
      oid: '2_5_4_15',
      value: ''
    }, {
      name: 'Common Name',
      oid: '2_5_4_3',
      value: ''
    }, {
      name: 'Country',
      oid: '2_5_4_6',
      value: ''
    }, {
      name: 'DN Qualifier',
      oid: '2_5_4_46',
      value: ''
    }, {
      name: 'Domain Component',
      oid: '0_9_2342_19200300_100_1_25',
      value: ''
    }, {
      name: 'Email',
      oid: '1_2_840_113549_1_9_1',
      value: ''
    }, {
      name: 'Generation Qualifier',
      oid: '2_5_4_44',
      value: ''
    }, {
      name: 'Given Name',
      oid: '2_5_4_42',
      value: ''
    }, {
      name: 'Initials',
      oid: '2_5_4_43',
      value: ''
    }, {
      name: 'Jurisdiction of Incorporation Country Name',
      oid: '1_3_6_1_4_1_311_60_2_1_3',
      value: ''
    }, {
      name: 'Jurisdiction of Incorporation State or Province Name',
      oid: '1_3_6_1_4_1_311_60_2_1_2',
      value: ''
    }, {
      name: 'Locality',
      oid: '2_5_4_7',
      value: ''
    }, {
      name: 'Name',
      oid: '2_5_4_41',
      value: ''
    }, {
      name: 'Organization',
      oid: '2_5_4_10',
      value: ''
    }, {
      name: 'Organizational Unit',
      oid: '2_5_4_11',
      value: ''
    }, {
      name: 'Postal Code',
      oid: '2_5_4_17',
      value: ''
    }, {
      name: 'Pseudonym',
      oid: '2_5_4_65',
      value: ''
    }, {
      name: 'Serial Number',
      oid: '2_5_4_5',
      value: ''
    }, {
      name: 'State or Province',
      oid: '2_5_4_8',
      value: ''
    }, {
      name: 'Street Address',
      oid: '2_5_4_9',
      value: ''
    }, {
      name: 'Surname',
      oid: '2_5_4_4',
      value: ''
    }, {
      name: 'Title',
      oid: '2_5_4_12',
      value: ''
    }, {
      name: 'X.500 Unique Identifier',
      oid: '2_5_4_45',
      value: ''
    }
  ];
}

/**
 * Get the types for the Subject Alternate Name extension
 *
 * @returns {array}    array of objects
 */
function getSubjectAlternateNameTypes () {
  var directoryNameTypes = getDirectoryNameTypes();

  return [
    {
      name: 'Other Name',
      oid: '',
      value: '',
      tag: 'a0',
      customFormData: {
        parsedPreview: '',
        parseFailed: false
      }
    }, {
      name: 'Email',
      value: '',
      tag: '81'
    }, {
      name: 'DNS Name',
      value: '',
      tag: '82'
    }, {
      name: 'Directory Name',
      types: directoryNameTypes,
      selected: directoryNameTypes[0],
      names: [],
      tag: 'a4'
    }, {
      name: 'URI',
      value: '',
      tag: '86'
    }, {
      name: 'IP Address',
      value: '',
      tag: '87'
    }
  ];
}

/**
 * Gets all the extensions that the user can select from
 *
 * @returns {array}    all standard X.509 v3 certificate extensions
 */
function getAllExtensions () {
  var hashTypes = getHashTypes();
  var authorityInformationAccessTypes = getAuthorityInformationAccessTypes();
  var crlDistributionPointsTypes = getCRLDistributionPointsTypes();
  var certificatePolicies = getCertificatePolicies();
  var certificatePolicyQualifiers = getCertificatePolicyQualifiers();
  var subjectAlternateNameTypes = getSubjectAlternateNameTypes();

  return [
    {
      name: 'Authority Information Access',
      oid: '1_3_6_1_5_5_7_1_1',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: false,
      customFormData: {
        types: authorityInformationAccessTypes,
        defaultItem: {
          type: authorityInformationAccessTypes[0],
          value: ''
        },
        items: []
      }
    }, {
      name: 'CRL Distribution Points',
      oid: '2_5_29_31',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: false,
      customFormData: {
        types: crlDistributionPointsTypes,
        defaultItem: {
          type: crlDistributionPointsTypes[0],
          value: ''
        },
        items: []
      }
    }, {
      name: 'Authority Key Identifier',
      oid: '2_5_29_35',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: false,
      customFormData: {
        options: hashTypes,
        selected: hashTypes[2]
      }
    }, {
      name: 'Basic Constraints',
      oid: '2_5_29_19',
      critical: true,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: false,
      customFormData: {
        ca: false,
        pathLengthConstraint: false,
        pathLengthValue: 0,
      }
    }, {
      name: 'Certificate Policies',
      oid: '2_5_29_32',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: false,
      customFormData: {
        policyTypes: certificatePolicies,
        selectedPolicy: certificatePolicies[0],
        qualifierTypes: certificatePolicyQualifiers,
        selectedQualifier: certificatePolicyQualifiers[0],
        policies: []
      }
    }, {
      name: 'Certificate Template Extension',
      oid: '1_3_6_1_4_1_311_21_7',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: true,
      customFormData: {
        parsedPreview: '',
        parseFailed: false
      }
    }, {
      name: 'Extended Key Usage',
      oid: '2_5_29_37',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: false,
      customFormData: {
        options: [
          {
            name: 'TLS Web Server Authentication',
            oid: '1_3_6_1_5_5_7_3_1',
            value: false
          }, {
            name: 'TLS Web Client Authentication',
            oid: '1_3_6_1_5_5_7_3_2',
            value: false
          }, {
            name: 'Code Signing',
            oid: '1_3_6_1_5_5_7_3_3',
            value: false
          }, {
            name: 'E-mail Protection',
            oid: '1_3_6_1_5_5_7_3_4',
            value: false
          }, {
            name: 'Time Stamping',
            oid: '1_3_6_1_5_5_7_3_8',
            value: false
          }, {
            name: 'Microsoft Individual Code Signing',
            oid: '1_3_6_1_4_1_311_2_1_21',
            value: false
          }, {
            name: 'Microsoft Commercial Code Signing',
            oid: '1_3_6_1_4_1_311_2_1_22',
            value: false
          }, {
            name: 'Microsoft Trust List Signing',
            oid: '1_3_6_1_4_1_311_10_3_1',
            value: false
          }, {
            name: 'Microsoft Server Gated Crypto',
            oid: '1_3_6_1_4_1_311_10_3_3',
            value: false
          }, {
            name: 'Microsoft Encrypted File System',
            oid: '1_3_6_1_4_1_311_10_3_4',
            value: false
          }, {
            name: 'Netscape Server Gated Crypto',
            oid: '2_16_840_1_113730_4_1',
            value: false
          }, {
            name: 'OCSP Signing',
            oid: '1_3_6_1_5_5_7_3_9',
            value: false
          }
        ]
      }
    }, {
      name: 'Issuer Alternate Name',
      oid: '2_5_29_18',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: true,
      customFormData: {
        parsedPreview: '',
        parseFailed: false
      }
    }, {
      name: 'Key Usage',
      oid: '2_5_29_15',
      critical: true,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: false,
      customFormData: {
        options: [
          {
            name: 'Digital Signature',
            value: false
          }, {
            name: 'Non Repudiation',
            value: false
          }, {
            name: 'Key Encipherment',
            value: false
          }, {
            name: 'Data Encipherment',
            value: false
          }, {
            name: 'Key Agreement',
            value: false
          }, {
            name: 'Certificate Sign',
            value: false
          }, {
            name: 'CRL Sign',
            value: false
          }, {
            name: 'Encipher Only',
            value: false
          }, {
            name: 'Decipher Only',
            value: false
          }
        ]
      }
    }, {
      name: 'MS Application Policies',
      oid: '1_3_6_1_4_1_311_21_10',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: true,
      customFormData: {
        parsedPreview: '',
        parseFailed: false,
      }
    }, {
      name: 'MS Template Name',
      oid: '1_3_6_1_4_1_311_20_2',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: true,
      customFormData: {
        parsedPreview: '',
        parseFailed: false,
      }
    }, {
      name: 'Name Constraints',
      oid: '2_5_29_30',
      critical: true,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: true,
      customFormData: {
        parsedPreview: '',
        parseFailed: false
      }
    }, {
      name: 'OCSP No-Check',
      oid: '1_3_6_1_5_5_7_48_4',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: true,
      customFormData: {
        parsedPreview: '',
        parseFailed: false
      }
    }, {
      name: 'Policy Constraints',
      oid: '2_5_29_36',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: true,
      customFormData: {
        parsedPreview: '',
        parseFailed: false
      }
    }, {
      name: 'Policy Mappings',
      oid: '2_5_29_33',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: true,
      customFormData: {
        parsedPreview: '',
        parseFailed: false
      }
    }, {
      name: 'Subject Alternate Name',
      oid: '2_5_29_17',
      critical: true,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: false,
      customFormData: {
        options: subjectAlternateNameTypes,
        selected: subjectAlternateNameTypes[0],
        names: [subjectAlternateNameTypes[0]]
      }
    }, {
      name: 'Subject Key Identifier',
      oid: '2_5_29_14',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: false,
      customFormData: {
        options: hashTypes,
        selected: hashTypes[2]
      }
    }, {
      name: 'Custom',
      oid: '',
      critical: false,
      mode: 'Uploaded',
      value: '',
      useDefaultForm: true,
      customFormData: {
        parsedPreview: '',
        parseFailed: false
      }
    }
  ];
}

/**
 * Get the map of extension mode display names
 *
 * @returns {object}    the map of extension mode display names
 */
function getV3ExtensionModes () {
  return {
    'None': -1,
    'Included': 0,
    'Not Included': 1,
    'Required': 2,
    'Fixed': 3,
    'Restricted': 4,
    'Uploaded': 5
  };
}

export default {
  getKnownDNProfile: getKnownDNProfile,
  getHashTypes: getHashTypes,
  getAuthorityInformationAccessTypes: getAuthorityInformationAccessTypes,
  getCRLDistributionPointsTypes: getCRLDistributionPointsTypes,
  getCertificatePolicies: getCertificatePolicies,
  getCertificatePolicyQualifiers: getCertificatePolicyQualifiers,
  getAllExtensions: getAllExtensions,
  getV3ExtensionModes: getV3ExtensionModes,
  getDirectoryNameTypes: getDirectoryNameTypes,
  getSubjectAlternateNameTypes: getSubjectAlternateNameTypes
};
