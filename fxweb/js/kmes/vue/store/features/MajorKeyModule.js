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

import Vue from 'vue';
import Vuex from 'vuex';

import MajorKeyApi from 'shared/api/MajorKeyApi';

import BalancedDeviceModule from 'kmes/store/features/BalancedDeviceModule';

let store = new Vuex.Store({
  state: {
    checksums: {
      MFK: '',
      PMK: '',
    },
  },
  mutations: {
    /**
     * Saves the retrieved check digits to the store.
     *
     * @param {Object} state - The MajorKey module's state
     * @param {Object} checksums - The major key names and checksums
     */
    saveKCVs (state, checksums) {
      let storedKeys = ['MFK', 'PMK'];

      storedKeys.forEach(key => {
        if (checksums[key]) {
          state.checksums[key] = checksums[key];
        }
      });
    },
  },
  actions: {
    /**
     * Retrieves the major key checksums and saves them to the state.
     *
     * @param {Object} state - The MajorKey module's state
     *        {function} state.commit - The state's commit function
     *
     * @returns A promise with no success argument and an error string for the failure case.
     */
    loadMajorKeyChecksums ({ commit }) {
      let appCard = BalancedDeviceModule.getters.appCard;

      let promise = null;
      if (appCard) {
        promise = MajorKeyApi.getMajorKeyChecksums(Vue.http, appCard);
        promise = promise.then((checksums) => {
          commit('saveKCVs', checksums);
        });
      } else {
        promise = Promise.reject(new Error('failed to load application card'));
      }

      return promise;
    }
  },
  getters: {
    /**
     * Retrieves the checksum map.
     *
     * @param {Object} state - The MajorKey module state
     *
     * @returns An object of {key_name: key_kcv} pairs
     */
    checksums (state) {
      return state.checksums;
    },
    /**
     * Retrieves an array of the major key names that are loaded.
     *
     * @param {Object} state - The Certificates module state
     *
     * @returns Array of loaded major keys
     */
    loaded (state) {
      let loaded = [];

      for (let key in state.checksums) {
        let kcv = state.checksums[key];
        if (kcv && kcv.length > 0) {
          loaded.push(key);
        }
      }

      return loaded;
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

  readyPromise = BalancedDeviceModule.ready();
  readyPromise = readyPromise.then(function () {
    return store.dispatch('loadMajorKeyChecksums');
  });

  return readyPromise;
}

export default {
  ready,
  getters: store.getters,
  dispatch: store.dispatch,
};
