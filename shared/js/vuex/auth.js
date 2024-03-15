import { useToast } from "vue-toastification";

import axios from "$shared/axios.js";
import { unwrapErr } from "$shared/utils/web";

const toast = useToast();
const makePerms = function (perms) {
  return {
    admin: perms.includes("ChMgmt:Administration"),
    database: perms.includes("ChMgmt:Database"),
    users: perms.includes("ChMgmt:Users"),
    roles: perms.includes("ChMgmt:Roles"),
    services: perms.includes("ChMgmt:Services"),
    logs: perms.includes("ChMgmt:Logs"),
    backup: perms.includes("ChMgmt:BackupRestore"),
    reboot: perms.includes("ChMgmt:Reboot"),
    hsms: perms.includes("ChMgmt:Hsms"),
    legacy:
      perms.includes("ChMgmt:Administration") ||
      perms.includes("ChMgmt:Database") ||
      perms.includes("ChMgmt:Logs") ||
      perms.includes("ChMgmt:BackupRestore") ||
      perms.includes("ChMgmt:Hsms"),
  };
};

export default {
  namespaced: true,
  state: {
    token: null,
    users: [],
    perms: [],
    auth_perms: [],
    roles: [],
    managed_roles: [],
    hardened: false,
    management: false,
    user_management: false,
    fully_logged_in: false,
    dualFactor: null,
    error: null,
    has_principal: false,
    remaining_logins: 2,
    mgmtPerms: makePerms([]),
  },
  mutations: {
    login(state, data) {
      state.token = data.token;
      state.users = data.users;
      state.perms = data.perms;
      state.auth_perms = data.authPerms;
      state.roles = data.roles;
      state.managed_roles = data.managedRoles;
      state.hardened = data.hardened;
      state.management = data.management;
      state.user_management = data.userManagement;
      state.fully_logged_in = data.fullyLoggedIn;
      state.dualFactor = data.dualFactor;
      state.has_principal = data.hasPrincipal;
      state.remaining_logins = data.remainingLogins;
      state.mgmtPerms = makePerms(data.authPerms);
      state.error = null;
    },
    logout(state) {
      state.token = null;
      state.users = [];
      state.perms = [];
      state.auth_perms = [];
      state.roles = [];
      state.managed_roles = [];
      state.hardened = false;
      state.management = false;
      state.user_management = false;
      state.fully_logged_in = false;
      state.dualFactor = null;
      state.error = null;
      state.has_principal = false;
      state.remaining_logins = 2;
      state.mgmtPerms = makePerms([]);
    },
    setError(state, error) {
      state.error = unwrapErr(error);
    },
  },
  actions: {
    async reload(context) {
      try {
        const loginReponse = await axios.get("/home/v1/login");
        if (loginReponse.data.users.length > 0) {
          context.commit("login", loginReponse.data);
        } else {
          window.sessionStorage.clear();
          context.commit("logout");
        }
      } catch (error) {
        if (error.response.status == 502) {
          toast.error("Reconnecting to web server...");

          // Wait 5s and retry
          setTimeout(function () {
            location.reload();
          }, 5000);
        } else {
          toast.error(unwrapErr(error));
        }
      }
    },

    async logout(context) {
      axios.get("/logout").catch(() => {}); // attempt HSM log out

      return axios.post("/home/v1/logout").then(() => {
        context.commit("logout");
      });
    },

    // Perform JWT login
    async tokenLogin(state, jwt) {
      try {
        await axios
          .post("/home/v1/login", {
            authType: "jwt",
            authCredentials: {
              token: jwt,
            },
          })
          .then(function () {
            // Reload auth state on success
            this.reload(state);
          });
        // Handle error
      } catch (err) {
        state.commit("setError", err);
      }
    },
    // Set logged out state
    doLogout(state) {
      state.commit("logout");
    },
  },
};
