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

import CardSchema from 'kmes/store/schema/CardSchema';
import CertAuthoritySchema from 'kmes/store/schema/CertAuthoritySchema';
import SymmetricKeySchema from 'kmes/store/schema/SymmetricKeySchema';
import TokenGroupSchema from 'kmes/store/schema/TokenGroupSchema';
import X509CertSchema from 'kmes/store/schema/X509CertSchema';

function createFromTypeString (objectType) {
  switch (objectType) {
    case 'TOKENGROUP':
      return new TokenGroupSchema();
    case 'KEY':
      return new SymmetricKeySchema();
    case 'CERTAUTHORITY':
      return new CertAuthoritySchema();
    case 'X509CERT':
      return new X509CertSchema();
    case 'CARD':
      return new CardSchema();
  }

  return null;
}

export default {
  createFromTypeString,
};
