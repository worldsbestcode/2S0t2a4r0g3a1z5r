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

class TokenGroupSchema extends ManagedObjectSchema {
  constructor () {
    super();

    this.objectType = 'TOKENGROUP';
    this.name = '';
    this.keyID = '-1';
    this.keyName = '';
    this.verifyLength = 0;
    this.tokenizeDate = false;
    this.tokenNamespace = ['Decimal'];
    this.useLuhn = false;
    this.maskedLength = 0;
    this.preserveLeading = 0;
    this.preserveTrailing = 0;
    this.staticLeading = '';
  }
}

export default TokenGroupSchema;
