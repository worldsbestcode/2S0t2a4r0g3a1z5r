import { createStore } from "vuex";

// Store modules
import AuthModule from "./auth.js";
import BalancerModule from "./balancer.js";

// Combine all the modules
const store = createStore({
  modules: {
    auth: AuthModule,
    balancer: BalancerModule,
  },
});

export default store;
