import axios from "axios";
import store from "@/store";
import { unwrapErr } from "@/utils/web";

export default {
  namespaced: true,
  state: {
    token: null,
    users: [],
    perms: [],
    roles: [],
    managed_roles: [],
    hardened: false,
    management: false,
    user_management: false,
    fully_logged_in: false,
    error: null,
  },
  mutations: {
    login(state, data) {
      state.token = data.token;
      state.users = data.users;
      state.perms = data.perms;
      state.roles = data.roles;
      state.managed_roles = data.managed_roles;
      state.hardened = data.hardened;
      state.management = data.management;
      state.user_management = data.user_management;
      state.fully_logged_in = data.fully_logged_in;
      state.error = null;
    },
    logout(state) {
      state.token = null;
      state.users = [];
      state.perms = [];
      state.roles = [];
      state.managed_roles = [];
      state.hardened = false;
      state.management = false;
      state.user_management = false;
      state.fully_logged_in = false;
      state.error = null;
    },
    setError(state, error) {
      state.error = unwrapErr(error);
    },
  },
  actions: {
    // Load current auth state
    async reload(state) {
      try {
        // Get auth status
        axios.get("/v1/login").then(function (res) {
          if (res.data.users.length > 0) {
            state.commit("login", res.data);
          } else {
            state.commit("logout");
          }
        });
        // Handle error
      } catch (err) {
        state.commit("setError", err);
      }
    },
    // Perform JWT login
    async tokenLogin(state, jwt) {
      try {
        // TODO: This will be /login once someone fixes my python code
        await axios
          .post("/v1/login/jwt", {
            authType: "jwt",
            authCredentials: {
              token: jwt,
            },
          })
          .then(function () {
            // Reload auth state on success
            store.dispatch("auth/reload");
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
