import { httpV2 } from "@/plugins";

class DefaultSession {
  constructor() {
    this.id = null;
    this.identities = [];
    this.loginComplete = false;
    this.roles = [];
    this.permissions = {};
  }

  login(id, identities, loginComplete, permissions, roles) {
    this.id = id || this.id;
    this.identities = identities || this.identities;
    this.loginComplete = loginComplete || this.loginComplete;
    this.permissions = permissions
      ? Object.fromEntries(permissions.map((permission) => [permission, true]))
      : this.permissions;
    this.roles = roles || this.roles;
  }
}

export default {
  namespaced: true,
  state: {
    clusters: [],
  },
  getters: {
    loggedInClusters: function (state) {
      return state.clusters.filter((x) => x.session.loginComplete);
    },
    loggedOutClusters: function (state) {
      return state.clusters.filter((x) => !x.session.loginComplete);
    },
  },
  mutations: {
    makeClusterSession: function (store, payload) {
      payload.cluster.session.login(payload.sessionId);
    },
    login: function (store, payload) {
      const sessionId = payload.cluster.session.id;
      const res = payload.response;
      payload.cluster.session.login(
        sessionId,
        res.identities,
        res.loginComplete,
        res.permissions,
        res.roles,
      );
    },
    replaceExistingCluster: function (store, newCluster) {
      this.state.clusters = this.state.clusters.map((oldCluster) =>
        oldCluster.id === newCluster.id ? newCluster : oldCluster,
      );
    },
    logout: function (store, cluster) {
      cluster.session = new DefaultSession();
    },
    setClusters: function (state, clusters) {
      state.clusters = clusters;
    },
    replaceCluster: function (state, cluster) {
      let clusterIndex = state.clusters.findIndex((x) => x.id === cluster.id);
      if (clusterIndex !== -1) {
        state.clusters.splice(clusterIndex, 1, cluster);
      }
    },
  },
  actions: {
    initializeClusters: async function (context) {
      let clustersData = await httpV2.get("/clusters", {
        errorContextMessage: "Failed to fetch clusters",
      });
      let clusters = clustersData.groups.filter((x) => x.deviceType === "HSM");
      for (let cluster of clusters) {
        cluster.session = new DefaultSession();
      }
      context.commit("setClusters", clusters);
    },

    synchronizeClusterSessions: async function (context) {
      let sessionsData = await httpV2.get("/clusters/sessions", {
        errorContextMessage: "Failed to fetch cluster sessions",
      });
      let sessions = sessionsData.sessions;
      for (let cluster of context.state.clusters) {
        let session = sessions.find((x) => x.group === cluster.id);
        if (session) {
          try {
            let sessionDetails = await httpV2.get(
              `/clusters/sessions/${session.id}/login`,
              {
                errorContextMessage: `Failed to fetch login status for "${cluster.name}"`,
              },
            );
            cluster.session.login(
              session.id,
              sessionDetails.identities,
              sessionDetails.loginComplete,
              sessionDetails.permissions,
              sessionDetails.roles,
            );
            context.commit("replaceCluster", cluster);
          } catch (error) {
            // Ignore
          }
        }
      }
    },

    addClusterDetails: async function (context) {
      for (let cluster of context.state.clusters) {
        try {
          let clusterWithDetails = await httpV2.get(`/clusters/${cluster.id}`, {
            errorContextMessage: `Failed to fetch cluster details for "${cluster.name}"`,
          });
          clusterWithDetails.session = cluster.session;
          context.commit("replaceCluster", clusterWithDetails);
        } catch (error) {
          cluster.clusterDetailsRequestFailed = true;
          context.commit("replaceCluster", cluster);
        }
      }
    },

    logoutCluster: async function (store, cluster) {
      await httpV2.post(
        "/clusters/sessions/" + cluster.session.id + "/logout",
        {},
        { silenceToastError: true },
      );
    },
    closeSession: async function (store, cluster) {
      await httpV2.delete("/clusters/sessions/" + cluster.session.id, {
        silenceToastError: true,
      });
      store.commit("logout", cluster);
    },
  },
};
