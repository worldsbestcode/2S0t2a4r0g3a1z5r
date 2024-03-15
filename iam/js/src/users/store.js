// Stores the state for a user create/edit operation

import axios from "axios";
import { useToast } from "vue-toastification";

import fxwebauthn from "$shared/utils/fxwebauthn";
import { download } from "$shared/utils/misc";

const toast = useToast();

export default {
  namespaced: true,
  state: {
    dirty: false,
    loaded: false,

    uuid: null,
    page: null,
    username: null,
    application: false,
    management: false,
    hardened: false,
    archive: false,
    passChangedTime: null,
    apiKeyChangedTime: null,
    passwordChange: false,
    newPassword: "",
    repeatPassword: "",
    givenName: null,
    surname: null,
    commonName: null,
    mobilePhone: null,
    mobileCarrier: null,
    email: null,
    locked: false,
    roles: [],
    selectedRoles: [],
    otpToken: null,
    otpSessionId: null,
    otpVerify: null,
    fidoToken: null,
    newFidoName: null,
    newApiKey: false,
    hasApiKey: false,
    authType: null,
    tlsProviders: [],
    jwtProviders: [],
    tlsProvider: null,
    jwtProvider: null,
  },
  mutations: {
    setBasicInfo(state, info) {
      state.uuid = info.uuid;
      state.username = info.name;
      state.application = info.application;
      state.management = info.management;
      state.hardened = info.hardened;
      state.archive = info.archive;
      if (info.authType === "A") {
        state.apiKeyChangedTime = info.passChangedTime;
        state.passChangedTime = "Not loaded";
      } else {
        state.apiKeyChangedTime = "Not loaded";
        state.passChangedTime = info.passChangedTime;
      }
      state.passwordChange = info.passwordChange;
      state.givenName = info.givenName;
      state.surname = info.surname;
      state.commonName = info.commonName;
      state.mobilePhone = info.mobilePhone;
      state.mobileCarrier = info.mobileCarrier;
      state.email = info.email;
      state.locked = info.locked;
      state.roles = info.roles;
      state.selectedRoles = [];
      for (const i in info.roles) {
        state.selectedRoles.push(info.roles[i].uuid);
      }
      state.newPassword = "";
      state.repeatPassword = "";
      state.otpToken = null;
      state.otpSessionId = null;
      state.otpVerify = null;
      state.fidoToken = null;
      state.newFidoName = null;
      state.hasApiKey = info.authType === "A";
      state.newApiKey = info.authType !== "A";
      state.authType = info.authType;
      state.tlsProvider = null;
      state.jwtProvider = null;

      // Identity providers
      for (const i in info.authMechanisms) {
        const authMech = info.authMechanisms[i];
        if (authMech.identityProvider.providerType == "JWT") {
          state.jwtProvider = authMech.uuid;
        } else if (authMech.identityProvider.providerType == "TLS") {
          state.tlsProvider = authMech.uuid;
        }
      }
    },
    setNew(state, user) {
      state.uuid = null;
      state.username = "";
      state.application = !user;
      state.management = user;
      state.hardened = user;
      state.archive = false;
      state.passChangedTime = null;
      state.passwordChange = false;
      state.givenName = null;
      state.surname = null;
      state.commonName = null;
      state.mobilePhone = null;
      state.mobileCarrier = null;
      state.email = null;
      state.locked = false;
      state.roles = [];
      state.selectedRoles = [];
      state.newPassword = "";
      state.repeatPassword = "";
      state.otpToken = null;
      state.otpSessionId = null;
      state.otpVerify = null;
      state.fidoToken = null;
      state.newFidoName = null;
      state.newApiKey = !user;
      state.hasApiKey = false;
      // PW or API key
      state.authType = user ? "P" : "A";
      state.tlsProvider = null;
      state.jwtProvider = null;
    },
    setLoaded(state, loaded) {
      state.loaded = loaded;
    },
    setDirty(state, dirty) {
      state.dirty = dirty;
    },
    setOtp(state, token) {
      state.otpToken = token;
    },
    setFido(state, info) {
      // TODO: Multiple allowed
      for (const i in info) {
        state.fidoToken = info[i].name;
      }
    },
    setIdp(state, results) {
      let tlsProviders = [{ value: null, label: "None" }];
      let jwtProviders = [{ value: null, label: "None" }];
      for (const i in results) {
        const idp = results[i];
        if (idp.providerType == "TLS") {
          tlsProviders.push({
            value: idp.uuid,
            label: idp.name,
          });
        } else if (idp.providerType == "JWT") {
          jwtProviders.push({
            value: idp.uuid,
            label: idp.name,
          });
        }
      }
      state.tlsProviders = tlsProviders;
      state.jwtProviders = jwtProviders;
    },
    addRole(state, role) {
      state.selectedRoles.push(role);
    },
    removeRole(state, role) {
      for (const i in state.selectedRoles) {
        if (state.selectedRoles[i] == role) {
          state.selectedRoles.splice(i, 1);
          break;
        }
      }
    },
  },
  actions: {
    async load(context, uuid) {
      context.commit("setLoaded", false);

      // Load basic info
      const basicInfo = await axios.get("/kmes/v8/identities/" + uuid);
      let info = basicInfo.data.response;
      info.uuid = uuid;
      context.commit("setBasicInfo", info);

      // Load managed roles
      await context.dispatch("managedRoles/init", null, { root: true });

      // Dual-factor
      if (!context.state.application) {
        // Load OTP
        if (!context.state.hardened) {
          const otpInfo = await axios.get("/iam/v1/otp/tokens/" + uuid);
          context.commit("setOtp", otpInfo.data.token);
        }

        // Load FIDO
        const fidoInfo = await axios.get("/iam/v1/fido/tokens/" + uuid);
        context.commit("setFido", fidoInfo.data.tokens);
      }
      // Load identity providers
      else {
        const idpInfo = await axios.get("/iam/v1/idp/stubs");
        context.commit("setIdp", idpInfo.data.results);
      }

      context.commit("setLoaded", true);
    },

    getHexPassword(context) {
      let passwordHex = "";
      for (let i = 0; i < context.state.newPassword.length; i++) {
        const charCode = context.state.newPassword.charCodeAt(i).toString(16);
        passwordHex += charCode.padStart(2, "0");
      }
      return passwordHex;
    },

    // Update user information
    async update(context) {
      let params = {};

      // Check OTP register
      if (context.state.otpSessionId !== null) {
        await axios
          .post("/iam/v1/otp/register/" + context.state.uuid, {
            sessionId: context.state.otpSessionId,
            verify: context.state.otpVerify,
          })
          .then(function () {
            toast.success("Successfully registered OTP.");
          });
        return;
      }

      // Check FIDO register
      if (context.state.newFidoName !== null) {
        if (context.state.newFidoName == "") {
          toast.error("Token name required.");
          throw new Error();
        }

        // Get challenge
        const challengeInfo = await axios.get(
          "/iam/v1/fido/register/" +
            context.state.uuid +
            "/" +
            context.state.newFidoName,
        );
        const sessionId = challengeInfo.data.sessionId;
        const challenge = challengeInfo.data.challenge;

        // Send to token
        let tokenResponse = "";
        try {
          tokenResponse = await fxwebauthn.registerNewCredential(
            context.state.username,
            challenge,
            context.state.username,
          );
        } catch (error) {
          toast.error(error.message);
          throw new Error();
        }

        // Finish registration
        const tokenInfo = await axios.post(
          "/iam/v1/fido/register/" + context.state.uuid,
          {
            sessionId: sessionId,
            response: tokenResponse,
          },
        );
        const origin = tokenInfo.data.origin;
        //const credentialId = tokenInfo.data.credentialId;
        toast.success("Registered FIDO token for " + origin);

        return;
      }

      // Check password change params
      const isPass =
        context.state.authType == "P" || context.state.authType == "N";
      if (isPass && context.state.newPassword != "") {
        if (context.state.newPassword != context.state.repeatPassword) {
          toast.error("Repeat password does not match.");
          throw new Error();
        }
        params.passwordHex = await context.dispatch("getHexPassword");
      }
      // New API key?
      else if (context.state.authType == "A") {
        params.apiKey = context.state.newApiKey;
      }
      // TLS provider
      else if (context.state.authType == "T" && context.state.tlsProvider) {
        params.identityProvider = context.state.tlsProvider;
      }
      // JWT provider
      else if (context.state.authType == "J" && context.state.jwtProvider) {
        params.identityProvider = context.state.jwtProvider;
      }

      // Modify params
      params = {
        ...params,
        locked: context.state.locked,
        archive: context.state.archive,
        surname: context.state.surname,
        givenName: context.state.givenName,
        commonName: context.state.commonName,
        mobilePhone: context.state.mobilePhone,
        mobileCarrier: context.state.mobileCarrier,
        email: context.state.email,
        roles: context.state.selectedRoles,
        passwordChange: isPass && context.state.passwordChange,
      };

      // PATCH
      context.commit("setDirty", false);
      await axios
        .patch("/kmes/v8/identities/" + context.state.uuid, params)
        .then(function (result) {
          if (result.data.response.apiKey) {
            download(
              result.data.response.apiKey,
              "api-key-" + context.state.username + ".txt",
            );
          }

          toast.success("Successfully updated.");
          context.commit("setLoaded", false);
          context.commit("setDirty", true);
        });
    },

    // No longer dirty
    undirty(context) {
      context.commit("setDirty", false);
    },

    // Toggle user's locked state
    async lockunlock(context, user) {
      context.commit("setDirty", false);
      let lock = !user.locked;
      let name = user.username;
      await axios
        .patch("/kmes/v8/identities/" + user.uuid, {
          locked: lock,
        })
        .then(function () {
          toast.success((lock ? "Disabled " : "Enabled ") + name);
          context.commit("setDirty", true);
        });
    },

    // Modify roles
    addRole(context, role) {
      context.commit("addRole", role);
    },
    removeRole(context, role) {
      context.commit("removeRole", role);
    },

    // Update user information
    async remove(context) {
      context.commit("setDirty", false);
      await axios
        .delete("/kmes/v8/identities/" + context.state.uuid)
        .then(function () {
          toast.success("Successfully removed.");
          context.commit("setLoaded", false);
          context.commit("setDirty", true);
        });
    },

    async loadNew(context, type) {
      context.commit("setNew", type === "user");
      // Load managed roles
      await context.dispatch("managedRoles/init", null, { root: true });
      // Load identity providers
      if (type != "user") {
        const idpInfo = await axios.get("/iam/v1/idp/stubs");
        context.commit("setIdp", idpInfo.data.results);
      }
    },

    async add(context) {
      // Modify params
      let params = {
        application: context.state.application,
        name: context.state.username,
        locked: context.state.locked,
        surname: context.state.surname,
        givenName: context.state.givenName,
        commonName: context.state.commonName,
        mobilePhone: context.state.mobilePhone,
        mobileCarrier: context.state.mobileCarrier,
        email: context.state.email,
        roles: context.state.selectedRoles,
      };

      // PW
      if (
        context.state.authType == "P" &&
        context.state.newPassword.length > 0
      ) {
        params.passwordHex = await context.dispatch("getHexPassword");
        params.passwordChange = context.state.passwordChange;
      }
      // API key
      else if (context.state.authType == "A") {
        params.apiKey = context.state.newApiKey;
      }
      // TLS provider
      else if (context.state.authType == "T") {
        params.identityProvider = context.state.tlsProvider;
      }
      // JWT provider
      else if (context.state.authType == "J") {
        params.identityProvider = context.state.jwtProvider;
      }

      // Remove null values
      for (const key in params) {
        if (params[key] === null) {
          delete params[key];
        }
      }

      // POST
      try {
        context.commit("setDirty", false);
        await axios.post("/kmes/v8/identities", params).then(function (result) {
          const isApp = context.state.application;
          const redir = isApp ? "apps" : "users";

          if (result.data.response.apiKey) {
            download(
              result.data.response.apiKey,
              "api-key-" + context.state.username + ".txt",
            );
          }

          toast.success("Successfully created.");
          context.commit("setLoaded", false);
          context.commit("setDirty", true);

          // Back to view
          //router.replace({ path: redir });
          window.location.href = "/iam/#/" + redir;
        });
      } catch {
        // Toast caught it
      }
    },
  },
};
