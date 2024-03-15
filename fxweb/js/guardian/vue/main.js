// main.js
import Vue from 'vue';
import VueResource from 'vue-resource';
import VueSelect from 'vue-select';
import fxComponents from 'shared/fx-components';
import * as uiv from 'uiv';

import EncodingUtils from 'shared/EncodingUtils';
import HsmGroupManagement from 'components/HsmGroupManagement';
import MajorKeyApi from 'shared/api/MajorKeyApi';
import utils from 'shared/utils';
import X509ServiceDefs from 'shared/X509ServiceDefs';

// Plugin Packages
Vue.use(VueResource);
Vue.use(uiv);
// Setup an event bus to talk to angular for alerts
const EventBus = new Vue();

Object.defineProperties(Vue.prototype, {
  $bus: {
    get: function () {
      return EventBus;
    }
  }
});

Vue.use(VueResource);
// Set by fxApp.js
Vue.http.options.root = window.api_prefix;
Vue.use(fxComponents);

// Package components
Vue.component('v-select', VueSelect);

// Custom XSRF fields
import axios from "axios";
axios.defaults.xsrfCookieName = 'FXSRF-TOKEN';
axios.defaults.xsrfHeaderName = 'X-FXSRF-TOKEN';
Vue.http.headers.common['X-FXSRF-TOKEN'] = utils.parseCookies('FXSRF-TOKEN').value;

// Package components
Vue.component('v-select', VueSelect);

// Current global components - once fully ported to vue, these should all be deleted
// When these only reside in other angular, they should be removed from here
Vue.component('hsm-group-management', HsmGroupManagement);

// Currently Vue instances are created inside angular components
// Only create a main Vue app here after AdminLTE and angular are fully removed
// var vm = new Vue({
// });

// Angular compatibility inject Vue into global scope
window.Vue = Vue;
// For js ported from angular (but still used in angular) expose the class here
window.Scaffolding = {
  downloadFile: utils.downloadFile,
  EncodingUtils,
  X509ServiceDefs,
  MajorKeyApi,
};
