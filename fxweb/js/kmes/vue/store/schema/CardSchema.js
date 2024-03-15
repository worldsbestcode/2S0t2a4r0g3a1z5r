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

import BalancedDeviceSchema from './BalancedDeviceSchema';

class CardSchema extends BalancedDeviceSchema {
  constructor () {
    super();

    this.objectType = 'CARD';
  }
}

export default CardSchema;
