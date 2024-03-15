/**
 * @section LICENSE
 *
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, L.P. 2018
 *
 * This file is imported early on in main.js, so that module initialization
 * happens before the router import, which imports all of our other components.
 *
 * One example of why is the Vuex module. Vue.use(Vuex) has to be called before
 * any Vuex.Store call, so instead of including it every time that we call
 * Vuex.Store, we import it one time at the top of main.js
 */

import * as uiv from 'uiv';
import VTooltip from 'v-tooltip';
import Vue from 'vue';
import VueResource from 'vue-resource';
import Vuex from 'vuex';

import FxComponents from 'shared/fx-components';

// Third-party modules
Vue.use(uiv);
Vue.use(VueResource);
Vue.use(Vuex);
Vue.use(VTooltip);

// Load the shared fx-components plugin
Vue.use(FxComponents);
