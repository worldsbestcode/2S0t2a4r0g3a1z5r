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
 * Gets major key checksums for a given object.
 *
 * @param {Object} http - Object supplying the http method send functions.
 * @param {Object} device - Balancded device information. Optional.
 */
function getMajorKeyChecksums (http, device) {
  var formData = {};
  if (device) {
    formData = {
      'objectType': device.objectType,
      'objectID': device.objectID,
      'objectParentID': device.parentID
    };
  }

  var message = {
    'method': 'retrieve',
    'name': 'major keys',
    'formData': formData,
  };

  return http.post(window.apipath('/formdata'), message).then(function (response) {
    var checksums = [];
    if (response.data.result === 'Success') {
      checksums = response.data.formData.checksums;
    } else {
      throw response.data.message;
    }
    return checksums;
  });
}

export default {
  getMajorKeyChecksums,
};
