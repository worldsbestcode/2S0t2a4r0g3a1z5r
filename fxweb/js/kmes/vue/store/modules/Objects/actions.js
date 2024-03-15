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

import MORepository from 'kmes/store/api/MORepository';

/**
 * Adds the given object remotely.
 *
 * @param {Object} state - The object module's state
 *        {function} state.commit - The current state's commit function
 * @param {Object} object - A single object to add to the server
 *
 * @returns An API promise with no response value on success
 */
function add ({ commit }, object) {
  return MORepository.add(object);
}

/**
 * Generates a remote deletion by id function for a given object type.
 *
 * @param {string} objectType - The object type to delete
 */
function deleteByID (objectType) {
  /**
   * Deletes the given object remotely.
   *
   * Also updates the local cache if the remote deltion was successful.
   *
   * @param {Object} state - The object module's state
   *        {function} state.commit - The current state's commit function
   * @param {string[]} ids - An array of DBIDs to remove.
   *
   * @returns An API promise with no response value on success
   */
  return function ({ commit }, ids) {
    let promise = MORepository.deleteByID(objectType, ids);
    return promise.then(function (response) {
      commit('deleteLocal', ids);
    });
  };
}

/**
 * Generates a function to load a given page for a given object type.
 *
 * @param {string} objectType - The object type to filter for
 */
function loadPage (objectType) {
  /**
   * Loads a chunk of objects to store in local cache.
   *
   * @param {Object} state - The object module's state
   *        {function} state.commit - The current state's commit function
   * @param {Object} filterInfo - Filter information
   *        {number} filterInfo.chunkIndex - The chunk index to filter for
   *        {number} filterInfo.chunkSize - The chunk size
   *        {string} filterInfo.sortByColumn - The column to sort by
   *
   * @returns An API filter promise that contains the returned
   *         objects and the pagination data on success.
   */
  return function ({ commit }, { chunkIndex, chunkSize, sortByColumn }) {
    let promise = MORepository.getChunk(objectType, [], chunkIndex, chunkSize, sortByColumn);
    return promise.then(function (response) {
      commit('addLocal', response.objects);
      return response;
    });
  };
}

/**
 * Generates a function retrieve objects by their IDs
 *
 * @param objectType The object type to filter for
 */
function getByIDs (objectType) {
  /**
   * Loads specific objects and stores them in local cache.
   *
   * @param Object The object module's state
   *        commit The current state's commit function
   * @param ids An array of IDs to query for
   *
   * @return A promise. success=pagination+objects, failure=error string
   */
  return function ({ commit }, ids) {
    let promise = MORepository.getByIDs(objectType, ids);
    return promise.then(function (response) {
      commit('addLocal', response.objects);
      return response;
    });
  };
}

/**
 * Retrieves all actions and applies the given object type to any which an object
 * type can be applied to.
 *
 * Applying an object type just makes it a way to use the function without passing
 * in the object type every time the function is called.
 *
 * @param {string} objectType - The ManagedObject type to apply
 *
 * @returns all actions in this module with the given type applied
 */
function applyType (objectType) {
  return {
    add,
    deleteByID: deleteByID(objectType),
    loadPage: loadPage(objectType),
    getByIDs: getByIDs(objectType),
  };
}

export default {
  applyType,
};
