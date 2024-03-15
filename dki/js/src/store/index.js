import { createStore } from "vuex";

import sharedModules from "$shared/vuex";

import PedInjectModule from "./pedinject.js";
import ServiceInfo from "./serviceinfo.js";

// Combine all the modules
const store = createStore({
  modules: {
    ...sharedModules,
    pedinject: PedInjectModule,
    serviceInfo: ServiceInfo,
  },
});

export default store;
