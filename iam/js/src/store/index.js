// Store modules

import { createStore } from "vuex";

import sharedModules from "$shared/vuex";

import IdPEdit from "@/idp/store.js";
import RoleEdit from "@/roles/store.js";
import ManagedRoles from "@/store/managed-roles.js";
import UserEdit from "@/users/store.js";

// Combine all the modules
const store = createStore({
  modules: {
    ...sharedModules,
    user: UserEdit,
    role: RoleEdit,
    idp: IdPEdit,
    managedRoles: ManagedRoles,
  },
});

export default store;
