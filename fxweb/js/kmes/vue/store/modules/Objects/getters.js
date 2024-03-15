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

/**
 * Retrieves an array of all objects currently stored in this state.
 *
 * @param {Object} state - This Vuex module's state
 *
 * @returns objects in this state, as an array
 */
function getDataAsArray (state) {
  var cas = [];
  for (var i in state.data) {
    cas.push(state.data[i]);
  }
  return cas;
}

/**
 * Retrieves a map of objects currently stored in this state.
 *
 * @param {Object} state - This Vuex module's state
 *
 * @returns objects in this state, as a map
 */
function getDataAsMap (state) {
  return state.data;
}

export default {
  dataArray: getDataAsArray,
  dataMap: getDataAsMap,
};
