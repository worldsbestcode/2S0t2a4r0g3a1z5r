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
import MORepository from './MORepository';
import Vue from 'vue';

/**
 * Retrieves a chunk of child ojects given the caID and certID
 *
 * @param {string} caID - The certificate authority ID
 * @param {string} certID - The parent certificate ID
 * @param {number} chunkIndex - The chunk index, starting at 0
 *
 * @returns promise for the object query
 */
function getCertChildren (caID, certID = '-1', chunkIndex = 0) {
  var clauses = [
    FilterService.createFullClause('X.509 certificate', 'ca ID', caID),
    FilterService.createFullClause('X.509 certificate', 'parent ID', certID),
  ];

  return MORepository.getChunk('X509CERT', clauses, chunkIndex);
}

/**
 * Imports the given certificate data.
 *
 * @param {string} caID - The CA to add the new cert to
 * @param {string} certID - The parent cert to add the new cert to. -1 if new cert is root.
 * @param {string} certData - The certificate data to import
 * @param {string} majorKey - The major key to encrypt certificate keys under
 *
 * @return A promise. success=newCertID, false=an error string
 */
function importCertificate (caID, certID, certData, majorKey) {
  let formData = {
    method: 'import',
    objectType: 'X509CERT',
    caID: caID,
    certData: certData
  };

  if (certID !== '-1') {
    formData.parentCertID = certID;
  }

  if (majorKey && majorKey.length > 0) {
    formData.majorKey = majorKey;
  }

  return Vue.http.post('/app/formdata', formData).then(function (response) {
    MORepository.checkObjectSuccess(response);

    return {
      newCertID: response.data.newCertID,
    };
  });
}

export default {
  getCertChildren,
  importCertificate,
};
