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
import _ from 'lodash';
import Toastr from 'vue-toastr';

import './VueModuleInit';
import router from './router';
import utils from 'shared/utils';

import 'bootstrap/dist/css/bootstrap.css';
// removed to allow use of v5
// import 'bootstrap/dist/css/bootstrap-theme.css';

import './css/main.scss';

require('vue-toastr/src/vue-toastr.scss');

// Add the csrf token to requests
Vue.http.headers.common['X-XSRF-TOKEN'] = utils.parseCookies('XSRF-TOKEN').value;

// Add global event bus
const bus = new Vue({});
Object.defineProperty(Vue.prototype, '$bus', {
  get: function () {
    return this.$root.bus;
  }
});

// Don't print out production warning in console
Vue.config.productionTip = false;

// Create the main app
var App = new Vue({
  router,
  components: {
    'vue-toastr': Toastr,
  },
  data: {
    bus,
  },
  mounted: function () {
    const self = this;

    // Event handler for toastr events
    var showAlert = function (text, type = 'success', position = 'toast-top-full-width', timeout = 4000) {
      const toast = self.$root.$refs.toastr;
      if (text !== '' && !_.some(toast.list[position], ['msg', text])) {
        toast.Add({
          msg: text,
          position: position,
          type: type,
          timeout: timeout
        });
      }
    };

    this.$bus.$on('showAlert', showAlert);
  },
});

// Mount the app after the page loads, so we have the #app element
window.addEventListener('load', function () {
  App.$mount('#app');
});
