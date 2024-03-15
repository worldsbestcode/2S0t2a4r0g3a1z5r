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

import Vuex from 'vuex';

import BalancedDeviceRole from 'kmes/store/schema/BalancedDeviceRole';
import Objects from 'kmes/store/modules/Objects';

let store = new Vuex.Store({
  modules: {
    Objects: Objects.createModule('CARD'),
  },
  getters: {
    /**
     * Retrieves a device marked as the application device.
     *
     * @param {Object} state - The vuex module state
     * @param {Object} getters - The vuex module getters
     *
     * @returns null=not found, not null=found
     */
    appCard (state, getters) {
      let dataArray = getters['Objects/dataArray'];
      return dataArray.find(card => card.currentRole === BalancedDeviceRole.APPDEVICE);
    },
  },
});

let readyPromise = null;

/**
 * Lets the caller know when this module is finished loading.
 *
 * @return A promise.
 */
function ready () {
  if (readyPromise) {
    return readyPromise;
  }

  readyPromise = store.dispatch({
    type: 'Objects/loadPage',
    chunkIndex: 0,
    sortByColumn: 'ipaddress'
  });

  return readyPromise;
}

export default {
  ready,
  getters: store.getters,
  dispatch: store.dispatch,
};
