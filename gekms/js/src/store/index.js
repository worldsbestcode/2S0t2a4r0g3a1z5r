import { createStore } from "vuex";

import sharedModules from "$shared/vuex";

const store = createStore({
  modules: sharedModules,
});

export default store;
