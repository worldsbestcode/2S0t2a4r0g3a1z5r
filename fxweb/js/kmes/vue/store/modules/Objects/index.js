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

import actions from './actions';
import getters from './getters';
import mutations from './mutations';

function state () {
  return {
    data: {},
  };
}

/**
 * Creates this module for the given object type.
 *
 * Different from most other modules, this module has to be created from
 * this function, to simplify how the actions are called.
 *
 * @param {string} objectType - the object type
 *
 * @returns The Vuex 'objects' module for the given object type.
 */
function createModule (objectType) {
  return {
    namespaced: true,
    state,
    actions: actions.applyType(objectType),
    mutations,
    getters,
  };
}

export default {
  createModule,
};
