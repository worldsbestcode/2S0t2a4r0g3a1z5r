/**
 * @file      KeyGroupSchema.js
 * @author    John Torres <jtorres@futurex.com>
 *
 * @section LICENSE
 *
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex, L.P.
 *
 * Copyright by:  Futurex, L.P. 2018
 *
 */

import ManagedObjectSchema from './ManagedObjectSchema';

class KeyGroupSchema extends ManagedObjectSchema {
  constructor () {
    super();

    this.objectType = 'KEY_GROUP';
    this.name = '';
    this.owner = '';
    this.address = '';
    this.retrievalMethod = '';
    this.keyTemplate = 0;
    this.keyPeriod = '';
  }
}

export default KeyGroupSchema;
