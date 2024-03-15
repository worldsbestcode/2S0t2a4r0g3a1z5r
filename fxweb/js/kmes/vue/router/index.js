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
import Router from 'vue-router';
import Main from '../components/main/Main';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Main',
      component: Main,
    }
  ]
});
