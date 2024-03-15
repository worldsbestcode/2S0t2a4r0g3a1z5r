// Stores the state for a role create/edit operation

import axios from "axios";
import { useToast } from "vue-toastification";

import fxwebauthn from "$shared/utils/fxwebauthn";
import { unwrapErr } from "$shared/utils/web";

const toast = useToast();

export default {
  namespaced: true,
  state: {
    dirty: false,
    loaded: false,
    // User or app role?
    users: true,

    uuid: null,
    page: null,
    name: null,
    externalName: null,

    requiredLogins: "1",

    management: false,
    hardened: false,
    archive: false,
    principal: "1",

    // Managed roles of role being edit (UUID only)
    subRoles: [],
    services: [],
    perms: [],

    upgradePerms: false,
    dualFactorRequired: null,

    webLogin: false,
    localLogin: false,
    apiLogin: false,
    restLogin: false,
    excryptLogin: false,
    kmipLogin: false,
  },
  mutations: {
    setBasicInfo(state, info) {
      state.uuid = info.uuid;
      state.name = info.name;
      state.requiredLogins = "" + info.requiredLogins;
      state.management = info.management;
      state.users = info.management;
      state.hardened = info.hardened;
      state.archive = info.archive;
      state.principal = info.principal ? "1" : "0";
      state.subRoles = [];
      for (const i in info.managedRoles)
        state.subRoles.push(info.managedRoles[i].uuid);
      state.services = [];
      for (const i in info.services) state.services.push(info.services[i].uuid);
      state.perms = [];
      for (const i in info.permissions) {
        const perm = info.permissions[i];
        if (perm.startsWith("ChMgmt:")) state.perms.push(perm.substr(7));
      }
      state.selectedRoles = [];
      state.dualFactorRequired = info.dualFactorRequired;
      state.externalName = info.externalName;
      state.upgradePerms = info.upgradePerms;
      state.localLogin = info.ports.includes("Client");
      state.restLogin = info.ports.includes("REST API");
      state.excryptLogin = info.ports.includes("Excrypt");
      state.kmipLogin = info.ports.includes("KMIP");
      state.apiLogin = state.excryptLogin || state.kmipLogin || state.apiLogin;
      state.webLogin = info.ports.includes("Web");
    },
    setNew(state, user) {
      state.users = user;
      state.uuid = null;
      state.name = "";
      state.externalName = "";
      state.requiredLogins = "1";
      state.management = user;
      state.hardened = false;
      state.archive = false;
      state.principal = "1";
      state.subRoles = [];
      state.services = [];
      state.perms = [];
      state.selectedRoles = [];
      state.upgradePerms = false;
      state.dualFactorRequired = "Available";
      state.webLogin = user;
      state.localLogin = user;
      state.apiLogin = !user;
      state.restLogin = !user;
      state.excryptLogin = !user;
      state.kmipLogin = !user;
    },
    setLoaded(state, loaded) {
      state.loaded = loaded;
    },
    setDirty(state, dirty) {
      state.dirty = dirty;
    },
    addRole(state, role) {
      state.subRoles.push(role);
    },
    removeRole(state, role) {
      for (const i in state.subRoles) {
        if (state.subRoles[i] == role) {
          state.subRoles.splice(i, 1);
          break;
        }
      }
    },
    addService(state, svc) {
      state.services.push(svc);
    },
    removeService(state, svc) {
      for (const i in state.services) {
        if (state.services[i] == svc) {
          state.services.splice(i, 1);
          break;
        }
      }
    },
  },
  actions: {
    async load(context, uuid) {
      context.commit("setLoaded", false);

      // Load basic info
      const basicInfo = await axios.get("/kmes/v8/roles/" + uuid);
      let info = basicInfo.data.response;
      info.uuid = uuid;
      context.commit("setBasicInfo", info);

      // Load managed roles
      await context.dispatch("managedRoles/init", null, { root: true });

      context.commit("setLoaded", true);
    },

    getPorts(context) {
      let ports = [];
      if (context.state.users) {
        if (context.state.webLogin) ports.push("Web");
        if (context.state.localLogin) ports.push("Client");
        if (context.state.apiLogin) {
          ports.push("Excrypt");
          ports.push("KMIP");
          ports.push("REST API");
        }
      } else {
        if (context.state.excryptLogin) ports.push("Excrypt");
        if (context.state.kmipLogin) ports.push("KMIP");
        if (context.state.restLogin) ports.push("REST API");
      }

      return ports;
    },

    getManagedRoles(context) {
      if (!context.state.users) return null;

      let managedRoles = [];
      if (context.state.subRoles.length > 0) {
        managedRoles = context.state.subRoles;
      }

      // If we manage anonymous / cerberus role, add to managed roles
      if (context.state.upgradePerms) {
        for (const i in context.rootState.managedRoles.managedRoles) {
          const role = context.rootState.managedRoles.managedRoles[i];
          if (
            role.name == "Anonymous" ||
            role.name == "CryptoHub Central App"
          ) {
            if (!managedRoles.includes(role.uuid)) {
              managedRoles.push(role.uuid);
            }
          }
        }
      }

      return managedRoles;
    },

    // Update user information
    async update(context) {
      // Modify params
      let params = {
        archive: context.state.archive,
        ports: await context.dispatch("getPorts"),
        externalName: context.state.externalName,
        upgradePerms: context.state.upgradePerms,
        requiredLogins: context.state.requiredLogins,
        managedRoles: await context.dispatch("getManagedRoles"),
        services: context.state.services,
        mgmtPermissions: await context.dispatch("getMgmtPerms"),
      };

      // Remove null values
      for (const key in params) {
        if (params[key] === null) {
          delete params[key];
        }
      }

      // PATCH
      context.commit("setDirty", false);
      await context.dispatch("managedRoles/dirty", null, { root: true });
      await axios
        .patch("/kmes/v8/roles/" + context.state.uuid, params)
        .then(function () {
          toast.success("Successfully updated.");
          context.commit("setLoaded", false);
          context.commit("setDirty", true);
        });
    },

    // No longer dirty
    undirty(context) {
      context.commit("setDirty", false);
    },

    // Modify roles
    addRole(context, role) {
      context.commit("addRole", role);
    },
    removeRole(context, role) {
      context.commit("removeRole", role);
    },
    // Modify services
    addService(context, role) {
      context.commit("addService", role);
    },
    removeService(context, role) {
      context.commit("removeService", role);
    },

    // Update user information
    async remove(context) {
      context.commit("setDirty", false);
      await context.dispatch("managedRoles/dirty", null, { root: true });
      await axios
        .delete("/kmes/v8/roles/" + context.state.uuid)
        .then(function () {
          toast.success("Successfully removed.");
          context.commit("setLoaded", false);
          context.commit("setDirty", true);
        });
    },

    async loadNew(context, type) {
      context.commit("setLoaded", false);
      context.commit("setNew", type === "user");

      // Load managed roles
      await context.dispatch("managedRoles/init", null, { root: true });

      context.commit("setLoaded", true);
    },

    getMgmtPerms(context) {
      let ret = [];
      for (const i in context.state.perms) {
        ret.push("ChMgmt:" + context.state.perms[i]);
      }
      return ret;
    },

    async add(context) {
      // Modify params
      let params = {
        name: context.state.name,
        hardened: context.state.hardened,
        principal: context.state.principal == "1",
        management: context.state.management,
        requiredLogins: context.state.requiredLogins,
        ports: await context.dispatch("getPorts"),
        externalName: context.state.externalName,
        upgradePerms: context.state.upgradePerms,
        services: context.state.services,
        mgmtPermissions: await context.dispatch("getMgmtPerms"),
      };

      // Remove null values
      for (const key in params) {
        if (params[key] === null) {
          delete params[key];
        }
      }

      // POST
      try {
        context.commit("setDirty", false);
        await context.dispatch("managedRoles/dirty", null, { root: true });
        await axios.post("/kmes/v8/roles", params).then(function (result) {
          const isApp = !context.state.users;
          const redir = isApp ? "partitions" : "roles";
          toast.success("Successfully created.");
          context.commit("setLoaded", false);
          context.commit("setDirty", true);

          // Back to view
          //router.replace({ path: "roles" });
          window.location.href = "/iam/#/" + redir;
        });
      } catch {
        // Toast caught it
      }
    },

    async unarchive(context) {
      // Modify params
      let params = {
        archive: false,
      };

      // POST
      try {
        context.commit("setDirty", false);
        await context.dispatch("managedRoles/dirty", null, { root: true });
        await axios
          .patch("/kmes/v8/roles/" + context.state.uuid, params)
          .then(function () {
            const isApp = !context.state.users;
            const redir = isApp ? "partitions" : "roles";
            toast.success("Successfully created.");
            context.commit("setLoaded", false);
            context.commit("setDirty", true);

            // Back to view
            //router.replace({ path: "roles" });
            window.location.href = "/iam/#/" + redir;
          });
      } catch {
        // Toast caught it
      }
    },
  },
};
