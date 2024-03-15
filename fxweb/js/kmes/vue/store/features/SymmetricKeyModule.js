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

import MORepository from 'kmes/store/api/MORepository';
import Objects from 'kmes/store/modules/Objects';

let store = new Vuex.Store({
  actions: {
    /**
     * Retrieves a chunk of child objects.
     *
     * @param {Object} state - The Certificates module's state
     *        {function} state.commit - The state's commit function
     *
     * @returns object filter result
     */
    loadAESEncryptionKeys ({ commit }) {
      let promise = MORepository.getAESEncryptionKeys();

      promise = promise.then(response => {
        commit('Objects/addLocal', response.objects);
      });

      return promise;
    },
  },
  modules: {
    Objects: Objects.createModule('KEY'),
  }
});

/**
 * Lets the caller know when this module is finished loading.
 *
 * @return A promise.
 */
function ready () {
  return new Promise((resolve, reject) => {
    resolve();
  });
}

export default {
  ready,
  getters: store.getters,
  dispatch: store.dispatch,
};
