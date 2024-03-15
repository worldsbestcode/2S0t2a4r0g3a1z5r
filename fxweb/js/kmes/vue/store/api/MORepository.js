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

import FilterService from 'shared/FilterService';
import ObjectFactory from 'kmes/store/utils/ObjectFactory';
import Vue from 'vue';

/**
 * Determines if an object query was successful or not.
 *
 * @param {Object} response - The response to the object query
 *
 * @returns true=success, false=failure
 */
function isObjectSuccess (response) {
  return response.data.result === 'Success';
}

/**
 * Retrieves an error from the given object response.
 *
 * This assumes that the object response actually represents an error.
 *
 * @param {Object} response - The response to receive the error from.
 *
 * @returns Error message from the response. A general error message if none is in the reponse.
 */
function getObjectError (response) {
  var error = response.data.message;

  if (!error) {
    error = 'Error performing server modification of object.';
  }

  return error;
}

/**
 * Checks to see if an object command was successful.
 *
 * If unsuccessful, throw an error, which will just be a string.
 *
 * @param response The response to check
 *
 * @throw string error if the response wasn't a success
 */
function checkObjectSuccess (response) {
  if (!isObjectSuccess(response)) {
    throw getObjectError(response);
  }
}

/**
 * Processes a filter request.
 *
 * Sends the filter, checks success, convets results to objects, returns.
 *
 * @param objectType The type of objects we're filtering for
 * @param filter The filter to use to query objects
 *
 * @return a promise. success=pagination+objects data, failure=error string
 */
function processFilterRequest (objectType, filter) {
  return Vue.http.post('/object', filter).then(function (response) {
    checkObjectSuccess(response);

    var objectData = response.data.objectData;
    var parsedData = objectData[objectType].map(function (item) {
      var jsonObject = JSON.parse(item);
      var parsedObject = ObjectFactory.createFromTypeString(jsonObject.objectType);
      if (parsedObject) {
        parsedObject.fromJSON(jsonObject);
      }
      return parsedObject;
    });

    return {
      pagination: objectData.LOG_FILTER,
      objects: parsedData,
    };
  });
}

/**
 * Retrieves a chunk of objects from the middleware.
 *
 * @param {string} objectType - The type of the object to filter for
 * @param {Object[]} clauses - The clauses to add to the filter
 * @param {number} chunkindex - The chunk index
 * @param {number} chunkSize - The size of the chunk
 * @param {string} sortByColumn - The column to sort by
 *
 * @return a promise. success=pagination+objects data, failure=error string
 */
function getChunk (objectType, clauses = [], chunkIndex = 0, chunkSize = 200, sortByColumn = 'name') {
  var request = FilterService.requestData(objectType);
  var ordering = FilterService.orderingData(chunkSize, chunkIndex, sortByColumn, true);
  var filter = FilterService.makeFilter(request, ordering, clauses);
  return processFilterRequest(objectType, filter);
}

/**
 * Deletes an object by id on the server
 *
 * @param {string} objectType - The type of the object to filter for
 * @param {string[]} ids - An array of DBIDs to delete
 *
 * @returns A promise. success=no parameter, failure=error message
 */
function deleteByID (objectType, ids) {
  var config = {
    body: {
      objectData: {
        [objectType]: ids,
      },
    },
  };

  return Vue.http.delete('/object', config).then(function (response) {
    checkObjectSuccess(response);
  });
}

/**
 * Queries objects by their IDs.
 *
 * @param objectType The type of the object to filter for
 * @param ids An array of object IDs to filter for
 *
 * @return a promise. success=pagination+objects data, failure=error string
 */
function getByIDs (objectType, ids) {
  let objectIDs = {
    [objectType]: ids.join(','),
  };

  var request = FilterService.requestData(objectType, null, objectIDs);
  var ordering = FilterService.orderingData(ids.length, 0, 'name');
  var filter = FilterService.makeFilter(request, ordering);
  return processFilterRequest(objectType, filter);
}

/**
 * Adds a new object to the server.
 *
 * @param {Object} objectData - The data for the object to add (ManagedObjectSchema).
 *
 * @returns A promise. success=no parameter, failure=error message
 */
function add (objectData) {
  var addQuery = {
    method: 'create',
    objectData: {
      [objectData.objectType]: [objectData],
    },
  };

  return Vue.http.post('/object', addQuery).then(function (response) {
    checkObjectSuccess(response);
  });
}

/**
 * Retrieves a chunk of AES encryption keys from the server.
 *
 * @returns a promise for the chunk filter.
 */
function getAESEncryptionKeys () {
  var clauses = [
    // KEY has to be a Device Encryption Key
    FilterService.createFullClause('KEY', 'type', '10'),
    // Key has to be AES
    FilterService.createFullClause('KEY', 'length', '4,5,6', 'AND', 'SET'),
  ];

  return getChunk('KEY', clauses);
}

export default {
  getChunk,
  deleteByID,
  getByIDs,
  add,
  getAESEncryptionKeys,
  checkObjectSuccess,
};
