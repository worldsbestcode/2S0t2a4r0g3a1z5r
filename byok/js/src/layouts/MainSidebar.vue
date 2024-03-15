<template>
  <nav class="main-sidebar">
    <div class="cluster-lists">
      <cluster-list
        :clusters="loggedInClusters"
        route-name="actions"
        text="LOGGED IN"
      />
      <cluster-list
        :clusters="loggedOutClusters"
        route-name="login"
        text="LOGGED OUT"
      />
    </div>

    <div class="finished">
      <button class="button blue-button" @click="logoutAllClusters()">
        FINISHED
      </button>
    </div>
  </nav>
</template>

<script>
import { mapGetters } from "vuex";
import ClusterList from "@/components/ClusterList.vue";

export default {
  name: "MainSidebar",
  components: {
    "cluster-list": ClusterList,
  },
  computed: {
    ...mapGetters({
      loggedInClusters: "byok/loggedInClusters",
      loggedOutClusters: "byok/loggedOutClusters",
    }),
    sessions: function () {
      return this.$store.state.byok.clusters.filter(
        (cluster) => cluster.session.id,
      );
    },
  },
  methods: {
    logoutAllClusters: async function () {
      for (let session of this.sessions) {
        await this.$store.dispatch("byok/logoutCluster", session);
        await this.$store.dispatch("byok/closeSession", session);
      }
      sessionStorage.clear();
      this.$router.replace({ name: "landing" });
    },
  },
};
</script>

<style scoped>
.main-sidebar {
  --finished-height: 75px;
  --cluster-list-left-padding: 1rem;
  width: var(--main-sidebar-width);
  position: fixed;
  top: var(--main-header-height);
  bottom: 0;
  background-color: rgba(241, 241, 241, 1);
  border-right: 1px solid var(--border-color);

  /* Put the shared app header's shadow on top of the sidebar */
  z-index: -1;
}

.cluster-lists {
  height: calc(100% - var(--finished-height));
  overflow-y: auto;
}

.finished {
  height: var(--finished-height);
  border-top: 1px solid var(--border-color);
  padding: 10px;
  position: relative;
  background: linear-gradient(
    180deg,
    rgb(249, 249, 249) 0%,
    rgb(241, 241, 241) 35%,
    rgb(238, 238, 238) 100%
  );
  /* Share border with the last cluster wrapper when overflow occurs */
  margin-top: -1px;
}

.finished > button {
  width: 100%;
  height: 100%;
  font-size: 20px;
}
</style>
