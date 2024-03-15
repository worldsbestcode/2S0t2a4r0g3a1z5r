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

/**
 * Adds the given objects to the local object cache.
 *
 * @param {Object} state - The object module's state
 * @param {Object[]} objects - An array of objects to add to the local store
 * @param {string} objects[].objectID - The object's unique ID
 */
function addLocal (state, objects) {
  objects.forEach(object => Vue.set(state.data, object.objectID, object));
}

/**
 * Removes objects with the given IDs from the local object cache.
 *
 * @param {Object} state - The object module's state
 * @param {string[]} ids - An array of DBIDs to remove
 */
function deleteLocal (state, ids) {
  ids.forEach(id => Vue.delete(state.data, id));
}

export default {
  addLocal,
  deleteLocal,
};
