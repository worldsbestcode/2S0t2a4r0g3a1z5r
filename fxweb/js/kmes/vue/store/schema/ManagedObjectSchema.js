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

import ObjectUtils from 'kmes/store/utils/ObjectUtils';

/**
 * Class that defines the schema/model for managed objects.
 */
class ManagedObjectSchema {
  constructor () {
    this.objectType = 'UNKNOWN';

    this.objectID = '-1';
    this.ownerID = '-1';
    this.parentID = '-1';
    this.hasChildren = false;
  }

  /**
   * Sets the properties of this object to those in the given object.
   *
   * Only the properties that are defined in this object are set from
   * the given data.
   */
  fromJSON (data) {
    ObjectUtils.assignDefined(this, data);
  }
}

export default ManagedObjectSchema;
