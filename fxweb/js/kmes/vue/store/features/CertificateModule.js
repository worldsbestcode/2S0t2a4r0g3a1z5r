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
import CertRepository from 'kmes/store/api/CertRepository';
import Objects from 'kmes/store/modules/Objects';

let store = new Vuex.Store({
  actions: {
    /**
     * Retrieves a chunk of child objects.
     *
     * @param {Object} state - The Certificates module's state
     *        {function} state.commit - The state's commit function
     * @param {Object} info - The filter parameters
     *        {string} info.caID - The certificate authority ID the children are under
     *        {string} info.certID - The ID of the certificate whose direct children will be filtered for
     *        {number} info.chunkIndex - The chunk index
     *
     * @returns object filter result
     */
    getCertChildren ({ commit }, { caID, certID, chunkIndex }) {
      let promise = CertRepository.getCertChildren(caID, certID, chunkIndex);
      return promise.then((response) => {
        commit('Objects/addLocal', response.objects);
        return response;
      });
    },
    /**
     * Imports a certificate.
     *
     * @param {Object} state - The Certificates module's state
     *        {function} state.commit - The state's commit function
     * @param {Object} info - The import parameters
     *        {string} caID - The certificate authority ID to import to
     *        {string} certID - The parent cert ID to import to
     *        {string} data - The certificate data
     *        {string} majorKey - The major key to import the certificate under
     *
     * @return A promise. success=newCertID, failure=error string
     */
    importCertificate ({ commit }, { caID, certID, data, majorKey }) {
      return CertRepository.importCertificate(caID, certID, data, majorKey);
    },
  },
  getters: {
    /**
     * Creates a map for finding children quicker.
     *
     * CA IDs map to a map of parent cert IDs to arrays of children.
     * {
     *    ca_id: {
     *         parent_cert_id: [children],
     *         ...
     *    },
     *    ...
     * }
     *
     * @param {Object} state - The Certificates module state
     *
     * @returns The populated map
     */
    parentMap (state) {
      let caMap = new Map();

      for (let id in state.Objects.data) {
        let cert = state.Objects.data[id];

        let certMap = caMap.get(cert.certAuthorityID);
        if (certMap === undefined) {
          certMap = new Map();
          caMap.set(cert.certAuthorityID, certMap);
        }

        let certChildren = certMap.get(cert.parentID);
        if (certChildren === undefined) {
          certChildren = [];
          certMap.set(cert.parentID, certChildren);
        }

        certChildren.push(cert);
      }

      return caMap;
    },
    /**
     * Retrieves a function to search for child certificates.
     *
     * @param {Object} state - The Certificates module state
     * @param {Object} getters - The Certificates module getters
     *
     * @returns A function
     */
    getChildrenOf (state, getters) {
      /**
       * Looks through the parentMap for objects that have the given ca id and parent id.
       *
       * @param {string} caID - The certificate authority container id
       * @param {string} certID - The parent certificate ID
       *
       * @returns An array of found children
       */
      return function (caID, certID) {
        let caMap = getters.parentMap;
        let found = [];

        let certMap = caMap.get(caID);
        if (certMap) {
          found = certMap.get(certID);
        }

        return found;
      };
    }
  },
  modules: {
    Objects: Objects.createModule('X509CERT'),
  }
});

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
