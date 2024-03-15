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
import CertType from './CertType';

class CertAuthoritySchema extends ManagedObjectSchema {
  constructor () {
    super();

    this.objectType = 'CERTAUTHORITY';
    this.name = '';
    this.pkiType = CertType.X509Cert.value;
    this.rootCertificateID = '-1';
  }

  get pkiTypeString () {
    return CertType.fromValue(this.pkiType).name;
  }
}

export default CertAuthoritySchema;
