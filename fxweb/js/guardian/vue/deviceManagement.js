import Vue from 'vue';

// Instantiate a vue instance to access the global bus
var ComponentVue = new Vue();

/**
 * Generate payload for getting data for guardian manage
 * @param obj the object to balance (group or device)
 * @param domain the domain to load settings from
 * @return the payload
 */
function manageLoadPayload (obj, domain) {
  return {
    method: 'retrieve',
    name: 'guardian manage',
    formData: {
      objectID: obj.objectID,
      parentID: obj.parentID,
      manager: obj.objectType,
      operation: 'load',
      domain: domain,
    },
  };
}

/**
 * Generate payload for setting data for guardian manage
 * @param obj the object to balance (group or device)
 * @param domain the domain to save settings from
 * @param settings the settings to write
 * @return the payload
 */
function manageSavePayload (obj, domain, settings) {
  return {
    method: 'retrieve',
    name: 'guardian manage',
    formData: {
      objectID: obj.objectID,
      parentID: obj.parentID,
      manager: obj.objectType,
      operation: 'save',
      domain: domain,
      settings: settings,
    },
  };
}

export default {

  loadSecuritySettings (obj, callback) {
    var payload = manageLoadPayload(obj, 'hsm security settings');
    Vue.http.post('formdata', payload).then(function (response) {
      if (response.body.result !== 'Success') {
        ComponentVue.$bus.$emit('showAlert', 'Error', response.body.message);
      } else if (response.body.formData.settings) {
        callback(response.body.formData.settings);
      }
    });
  },

  saveSecuritySettings (obj, settings, callback) {
    var payload = manageSavePayload(obj, 'hsm security settings', settings);
    Vue.http.post('formdata', payload).then(function (response) {
      if (response.body.result !== 'Success') {
        ComponentVue.$bus.$emit('showAlert', 'Error', response.body.message);
      } else {
        ComponentVue.$bus.$emit('showAlert', 'OK', 'Security settings successfully changed');
      }
    });
  },

};
