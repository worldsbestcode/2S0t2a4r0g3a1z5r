import { createStore } from "vuex";

import sharedModules from "$shared/vuex";

import ByokModule from "@/store/byok.js";

const store = createStore({
  modules: {
    ...sharedModules,
    byok: ByokModule,
  },
});

export default store;
