// Holds information about the roles that we are able to manage

import axios from "axios";

export default {
  namespaced: true,
  state: {
    loaded: false,
    managedRoles: [],
    managedServices: [],
  },
  mutations: {
    setManagedRoles(state, info) {
      state.managedRoles = info;
    },
    setManagedServices(state, info) {
      state.managedServices = info;
    },
    setLoaded(state, loaded) {
      state.loaded = loaded;
    },
  },
  actions: {
    async init(context) {
      if (!context.state.loaded) {
        try {
          const roleInfo = await axios.get("/iam/v1/managed-roles");
          context.commit("setManagedRoles", roleInfo.data.managedRoles);
          context.commit("setManagedServices", roleInfo.data.managedServices);
          context.commit("setLoaded", true);
        } catch {
          // Toast caught it
        }
      }
    },
    async dirty(context) {
      await context.commit("setLoaded", false);
    },
  },
};
