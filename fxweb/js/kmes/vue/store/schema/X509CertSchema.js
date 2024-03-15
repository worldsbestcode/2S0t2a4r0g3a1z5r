/**
 * @section LICENSE
 *
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, L.P. 2018
 */

import ManagedObjectSchema from './ManagedObjectSchema';

class X509CertSchema extends ManagedObjectSchema {
  constructor () {
    super();

    this.objectType = 'X509CERT';
    this.certAuthorityID = '-1';
    this.displayName = '';
    this.majorKey = 'MFK';

    this.certificate = {
      tbsCertificate: {
        version: 3,
        serialNumber: '',
        issuer: '',
        subject: '',
        validity: {
          notBefore: '1970-01-01 00:00:00',
          notAfter: '1970-01-01 00:00:00',
        },
        publicKey: {
          type: '',
          modulus: '',
          exponent: '',
          curve: ''
        },
        issuerUniqueId: '',
        subjectUniqueId: '',
        // Extensions: { critical (Boolean), oid (String), value (String), parsedExt (Object) }
        extensions: [],
      },
      signatureAlgorithm: {
        encryptionAlgorithm: 'RSA',
        hashType: 'SHA-1',
      },
      signature: '',
      // Fingerprints: Strings
      fingerprints: [],
    };
  }
}

export default X509CertSchema;
