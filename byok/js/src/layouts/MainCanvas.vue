<template>
  <div class="main-canvas">
    <router-view :current-cluster="activeCluster" @close="navigateToActions" />
  </div>
</template>

<script>
import { clusterSessionExpired } from "@/utils/misc.js";
export default {
  name: "MainCanvas",
  provide: function () {
    return {
      getSessionId: () => this.activeCluster.session.id,
      isGpMode: () => this.activeCluster.features.includes("GP"),
      canCskl: () => this.activeCluster.features.includes("CSKL"),
      isExcryptTouch: () => {
        return new Promise((resolve) => {
          setTimeout(async () => {
            try {
              resolve(await window.fxctx.keys.isExcryptTouch());
            } catch (error) {
              resolve(false);
            }
          }, 100);
        });
      },
    };
  },
  data: function () {
    return {
      pollIntervalToken: null,
    };
  },
  computed: {
    activeCluster: function () {
      // used by old code -> currentCluster.session.id
      let chosen = { session: { identities: [] } };
      let clusters = this.$store.state.byok.clusters;
      for (let cluster of clusters) {
        if (cluster.id === this.$route.params.clusterId) {
          chosen = cluster;
        }
      }
      return chosen;
    },
  },
  beforeUnmount: function () {
    clearInterval(this.pollIntervalToken);
  },
  mounted: function () {
    this.pollAuthState();
    this.pollIntervalToken = setInterval(this.pollAuthState, 30 * 1000);
  },
  methods: {
    navigateToActions: function () {
      this.$router.push({ name: "actions" });
    },
    pollAuthState: function () {
      const cluster = this.activeCluster;
      if (!cluster || !cluster.session || !cluster.session.loginComplete) {
        return;
      }
      const loginUri = `/clusters/sessions/${cluster.session.id}/login`;
      this.$httpV2
        .get(loginUri, { errorContextMessage: "Failed to check login status" })
        .then((result) => {
          // Skip if we are still logged in, or we've logged out already while API call was in-flight
          if (result.loginComplete || !cluster.session.loginComplete) {
            return;
          }
          // We thought we were logged in but now hsm says we're not anymore
          clusterSessionExpired();
        });
    },
  },
};
</script>
