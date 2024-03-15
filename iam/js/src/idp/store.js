// Stores the state for an identity provider create/edit operation

import axios from "axios";
import { useToast } from "vue-toastification";

const toast = useToast();

const EXISTING_PASSWORD = "********";

export default {
  namespaced: true,
  state: {
    dirty: false,
    loaded: false,
    providerType: null,

    // Shared
    uuid: null,
    requireLocal: true,
    unionRoles: true,
    enforceDualFactor: true,

    // Similar
    userIdType: null,
    roleIdType: null,
    userField: null,
    roleField: null,

    // JWT
    jwtAuthType: null,
    hmacKey: null,
    pkiVerifyCert: null,
    jwksUrl: null,
    jwksTlsCa: null,
    issuer: null,
    maxValidity: null, // Ignoring this option cause it confused people
    leeway: 0,
    rolesFromToken: null,
    authorizedRoles: [],
    claims: [],

    // LDAP
    lookupMethod: null, // Ignoring this option
    loginMode: null,
    servers: [],
    tlsProfile: null,
    ldapTlsCa: null,
    ldapVersion: 3,
    adminUser: null,
    adminPassword: null,
    userBaseDn: null,
    memberOfField: null,
    roleBaseDn: null,
    memberField: null,
    lockoutThreshold: 0,
    lockoutPeriod: null,
  },
  mutations: {
    setInfo(state, info) {
      state.providerType = info.providerType;
      state.uuid = info.uuid;
      state.name = info.name;
      state.requireLocal = !info.allowExternal;
      state.unionRoles = info.unionRoles;
      state.enforceDualFactor = info.enforceDualFactor;

      if (info.providerType == "JWT") {
        state.userIdType = info.params.userIdType;
        state.jwtAuthType = info.params.jwtAuthType;
        state.roleIdType = info.params.roleIdType;
        state.issuer = info.params.issuer;
        state.maxValidity = info.params.maxValidity;
        state.leeway = info.params.leeway;
        if (state.jwtAuthType == "HMAC") state.hmacKey = EXISTING_PASSWORD;
        state.jwksUrl = info.params.jwksUrl;
        state.jwksTlsCa = info.params.jwksTlsCa;
        state.pkiVerifyCert = info.params.pkiVerifyCert;
        state.userField = info.params.userField;
        state.rolesFromToken = info.params.rolesFromToken
          ? "Token"
          : "Database";
        state.roleField = info.params.roleField;
        state.authorizedRoles = info.params.authorizedRoles; // XXX: [uuid, name]
        state.claims = info.params.claims;
      } else if (info.providerType == "LDAP") {
        state.userIdType = info.params.userIdType;
        state.roleIdType = info.params.roleIdType;
        state.lookupMethod = info.params.lookupMethod;
        state.loginMode = info.params.loginMode;
        state.tlsProfile = info.params.tlsProfile;
        state.ldapTlsCa = info.params.ldapTlsCa;
        state.ldapVersion = info.params.ldapVersion;
        state.adminUser = info.params.adminUser;
        state.adminPassword = EXISTING_PASSWORD;
        state.userBaseDn = info.params.userBaseDn;
        state.userField = info.params.userField;
        state.memberOfField = info.params.memberOfField;
        state.roleBaseDn = info.params.roleBaseDn;
        state.roleField = info.params.roleField;
        state.memberField = info.params.memberField;
        state.lockoutThreshold = info.params.lockoutThreshold;
        state.lockoutPeriod = info.params.lockoutPeriod;
        // Always put 3 servers so UI works
        state.servers = info.params.servers;
        while (state.servers.length < 3) state.servers.push("");
      }
    },
    setNew(state, type) {
      state.name = null;
      state.uuid = null;
      state.providerType = type;
      state.requireLocal = true;
      state.unionRoles = true;
      state.enforceDualControl = true;

      state.userIdType = "Username";
      state.roleIdType = "Name";
      state.userField = null;
      state.roleField = null;

      if (type == "JWT") {
        state.jwtAuthType = "HMAC";
        state.hmacKey = null;
        state.pkiKey = null;
        state.jwksUrl = null;
        state.jwksTlsCa = null;
        state.pkiVerifyCert = null;
        state.issuer = null;
        state.maxValidity = null;
        state.leeway = 30;
        state.rolesFromToken = "Token";
        state.authorizedRoles = [];
        state.claims = [];
        state.userField = "sub";
        state.roleField = "roles";
      } else if (type == "LDAP") {
        state.userIdType = "Username";
        state.roleIdType = "Name";
        state.lookupMethod = "Search DN";
        state.loginMode = "Simple";
        state.servers = ["", "", ""];
        state.tlsProfile = null;
        state.ldapTlsCa = null;
        state.ldapVersion = 3;
        state.adminUser = null;
        state.adminPassword = null;
        state.userBaseDn = null;
        state.userField = "cn";
        state.memberOfField = "memberOf";
        state.roleBaseDn = null;
        state.roleField = "cn";
        state.memberField = "member";
        state.lockoutThreshold = 3;
        state.lockoutPeriod = "20 Seconds";
      }
    },
    setLoaded(state, loaded) {
      state.loaded = loaded;
    },
    setDirty(state, dirty) {
      state.dirty = dirty;
      if (dirty) state.hmacKey = null;
    },
  },
  actions: {
    async load(context, uuid) {
      context.commit("setLoaded", false);

      const response = await axios.get("/iam/v1/idp/" + uuid);
      context.commit("setInfo", response.data);

      context.commit("setLoaded", true);
    },

    getAdminPwHex(context) {
      let passwordHex = "";
      for (let i = 0; i < context.state.adminPassword.length; i++) {
        const charCode = context.state.adminPassword.charCodeAt(i).toString(16);
        passwordHex += charCode.padStart(2, "0");
      }
      return passwordHex;
    },

    // Modify IDP
    async update(context) {
      // Modify params
      let params = {
        providerType: context.state.providerType,
        name: context.state.name,
        allowExternal: !context.state.requireLocal,
        unionRoles: context.state.unionRoles,
        enforceDualFactor: context.state.enforceDualFactor,
      };

      if (context.state.providerType == "JWT") {
        params.params = {
          userIdType: context.state.userIdType,
          roleIdType: context.state.roleIdType,
          userField: context.state.userField,
          roleField: context.state.roleField,
          jwtAuthType: context.state.jwtAuthType,
          issuer: context.state.issuer,
          leeway: context.state.leeway,
          rolesFromToken: context.state.rolesFromToken == "Token",
          //authorizedRoles:
          claims: context.state.claims,
        };

        // Auth
        if (
          context.state.jwtAuthType == "HMAC" &&
          context.state.hmacKey &&
          context.state.hmacKey != EXISTING_PASSWORD
        ) {
          params.params.hmacKey = context.state.hmacKey;
        } else if (context.state.jwtAuthType == "PKI") {
          params.params.pkiKey = context.state.pkiKey;
          params.params.pkiVerifyCert = context.state.pkiVerifyCert;
        } else if (context.state.jwtAuthType == "URL") {
          params.params.jwksUrl = context.state.jwksUrl;
          params.params.jwksTlsCa = context.state.jwksTlsCa;
        }

        // Yeet empty claims
        for (let i = 0; i < params.params.claims.length; i++) {
          const claim = params.params.claims[i];
          for (let j = 0; j < params.params.claims.length; j++) {
            if (claim.values.length === 0) claim.values.splice(j--, 1);
          }
          if (claim.values.length === 0) params.params.claims.splice(i--, 1);
        }
      } else if (context.state.providerType == "LDAP") {
        // Remove empty server addresses
        for (let i = 0; i < context.state.servers.length; i++) {
          if (!context.state.servers[i]) context.state.servers.splice(i--, 1);
        }
        params.params = {
          userIdType: context.state.userIdType,
          roleIdType: context.state.roleIdType,
          lookupMethod: context.state.lookupMethod,
          loginMode: context.state.loginMode,
          servers: context.state.servers,
          tlsProfile: context.state.tlsProfile,
          ldapTlsCa: context.state.ldapTlsCa,
          ldapVersion: context.state.ldapVersion,
          adminUser: context.state.adminUser,
          userBaseDn: context.state.userBaseDn,
          userField: context.state.userField,
          memberOfField: context.state.memberOfField,
          roleBaseDn: context.state.roleBaseDn,
          roleField: context.state.roleField,
          memberField: context.state.memberField,
          lockoutThreshold: context.state.lockoutThreshold,
          lockoutPeriod: context.state.lockoutPeriod,
        };
        if (
          context.state.adminPassword &&
          context.state.adminPassword != EXISTING_PASSWORD
        ) {
          params.params.adminPasswordHex =
            await context.dispatch("getAdminPwHex");
        }
      }

      // Remove null values
      for (const key in params) {
        if (params[key] === null || params[key] === "") {
          delete params[key];
        }
      }
      for (const key in params.params) {
        if (params.params[key] === null || params.params[key] === "") {
          delete params.params[key];
        }
      }

      // PATCH
      context.commit("setDirty", false);
      try {
        await axios
          .patch("/iam/v1/idp/" + context.state.uuid, params)
          .then(function (result) {
            toast.success("Successfully updated.");
            context.commit("setLoaded", false);
            context.commit("setDirty", true);
          });

        // Back to view
        //router.replace({ path: "idp" });
        window.location.href = "/iam/#/idp";
      } catch {
        // toast handled the error
      }
    },

    // No longer dirty
    undirty(context) {
      context.commit("setDirty", false);
    },

    // Update user information
    async remove(context) {
      context.commit("setDirty", false);
      await axios.delete("/iam/v1/idp/" + context.state.uuid).then(function () {
        toast.success("Successfully removed.");
        context.commit("setLoaded", false);
        context.commit("setDirty", true);
      });
    },

    async loadNew(context, type) {
      context.commit("setNew", type);
    },

    async add(context) {
      // Add params
      let params = {
        providerType: context.state.providerType,
        name: context.state.name,
        allowExternal: !context.state.requireLocal,
        unionRoles: context.state.unionRoles,
        enforceDualFactor: context.state.enforceDualFactor,
      };

      // JWT params
      if (context.state.providerType == "JWT") {
        params.params = {
          userIdType: context.state.userIdType,
          roleIdType: context.state.roleIdType,
          userField: context.state.userField,
          roleField: context.state.roleField,
          jwtAuthType: context.state.jwtAuthType,
          issuer: context.state.issuer,
          leeway: context.state.leeway,
          rolesFromToken: context.state.rolesFromToken == "Token",
          //authorizedRoles:
          claims: context.state.claims,
        };

        // Auth
        if (context.state.jwtAuthType == "HMAC" && context.state.hmacKey) {
          params.params.hmacKey = context.state.hmacKey;
        } else if (context.state.jwtAuthType == "PKI") {
          params.params.pkiKey = context.state.pkiKey;
          params.params.pkiVerifyCert = context.state.pkiVerifyCert;
        } else if (context.state.jwtAuthType == "URL") {
          params.params.jwksUrl = context.state.jwksUrl;
          params.params.jwksTlsCa = context.state.jwksTlsCa;
        }

        // Yeet empty claims
        for (let i = 0; i < params.params.claims.length; i++) {
          const claim = params.params.claims[i];
          for (let j = 0; j < params.params.claims.length; j++) {
            if (claim.values.length === 0) claim.values.splice(j--, 1);
          }
          if (claim.values.length === 0) params.params.claims.splice(i--, 1);
        }
      }
      // LDAP params
      else if (context.state.providerType == "LDAP") {
        // Remove empty server addresses
        for (let i = 0; i < context.state.servers.length; i++) {
          if (!context.state.servers[i]) context.state.servers.splice(i--, 1);
        }
        params.params = {
          userIdType: context.state.userIdType,
          roleIdType: context.state.roleIdType,
          lookupMethod: context.state.lookupMethod,
          loginMode: context.state.loginMode,
          servers: context.state.servers,
          tlsProfile: context.state.tlsProfile,
          ldapTlsCa: context.state.ldapTlsCa,
          ldapVersion: context.state.ldapVersion,
          adminUser: context.state.adminUser,
          userBaseDn: context.state.userBaseDn,
          userField: context.state.userField,
          memberOfField: context.state.memberOfField,
          roleBaseDn: context.state.roleBaseDn,
          roleField: context.state.roleField,
          memberField: context.state.memberField,
          lockoutThreshold: context.state.lockoutThreshold,
          lockoutPeriod: context.state.lockoutPeriod,
        };

        if (
          context.state.adminPassword &&
          context.state.adminPassword != EXISTING_PASSWORD
        ) {
          params.params.adminPasswordHex =
            await context.dispatch("getAdminPwHex");
        }
      }

      // Remove null values
      for (const key in params) {
        if (params[key] === null || params[key] === "") {
          delete params[key];
        }
      }
      for (const key in params.params) {
        if (params.params[key] === null || params.params[key] === "") {
          delete params.params[key];
        }
      }

      // POST
      try {
        context.commit("setDirty", false);
        await axios.post("/iam/v1/idp", params).then(function (result) {
          toast.success("Successfully created.");
          context.commit("setLoaded", false);
          context.commit("setDirty", true);

          // Back to view
          //router.replace({ path: "idp" });
          window.location.href = "/iam/#/idp";
        });
      } catch {
        // Toast caught it
      }
    },
  },
};
