<template>
  <div v-if="clusters.length > 0">
    <p class="cluster-list-section-text">{{ text }}</p>
    <ul class="cluster-list">
      <div
        v-for="cluster in clusters"
        :key="cluster.id"
        :class="[
          'cluster-wrapper',
          isActiveCluster(cluster.id) && 'active-cluster',
        ]"
      >
        <router-link
          :to="{ name: routeName, params: { clusterId: cluster.id } }"
          class="cluster-item"
          :cluster="cluster"
        >
          <p :title="cluster.name">{{ cluster.name }}</p>

          <div class="icons">
            <i class="fa fa-server" />
            <span>{{ cluster.deviceCount }}</span>
            <i class="fa fa-user" />
            <span>{{ cluster.session.identities.length }}</span>
            <i
              v-if="cluster.clusterDetailsRequestFailed"
              title="Failed to fetch cluster details."
              class="fas fa-exclamation-triangle"
            />
          </div>
        </router-link>
        <button
          v-if="
            cluster.session.identities && cluster.session.identities.length > 0
          "
          class="cluster-item-close"
          @click="logoutCluster(cluster)"
        >
          <i class="inner-close fa fa-times" />
        </button>
      </div>
    </ul>
  </div>
</template>

<script>
export default {
  props: {
    routeName: {
      type: String,
      required: true,
    },
    clusters: {
      type: Array,
      required: true,
    },
    text: {
      type: String,
    },
  },
  methods: {
    isActiveCluster: function (clusterId) {
      return clusterId === this.$route.params.clusterId;
    },
    logoutCluster: async function (cluster) {
      await this.$store.dispatch("byok/logoutCluster", cluster);
      await this.$store.dispatch("byok/closeSession", cluster);
      if (this.isActiveCluster(cluster.id)) {
        this.$router.replace({ name: "login" });
      }
    },
  },
};
</script>

<style scoped>
.cluster-list {
  --close-button-width: 32px;
  padding: 0;
  margin: 0;
  list-style-type: none;
}

.cluster-list-section-text {
  margin-bottom: 0;
  background-color: var(--text-color);
  color: white;
  font-size: 10px;
  font-weight: bold;
  height: 1.5rem;
  display: flex;
  align-items: center;
  padding-left: var(--cluster-list-left-padding);
}

.cluster-wrapper {
  display: flex;
  border-top: 1px solid var(--border-color);
  background: linear-gradient(to bottom, #f9f9f9 5%, #e9e9e9 100%);
}

.cluster-wrapper:last-child {
  border-bottom: 1px solid var(--border-color);
}

.active-cluster {
  background-image: linear-gradient(to top, #0088cc, #0044cc);
  color: white;
}

.cluster-item {
  flex-grow: 1;
  text-decoration: none;
  font-size: 13px;
  color: inherit;
  padding: 0.4rem;
  padding-left: var(--cluster-list-left-padding);
}

.cluster-item p {
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cluster-item-close {
  border: 0;
  border-left: 1px solid var(--border-color);
  padding: 0;
  background-color: transparent;
  color: inherit;
  width: var(--close-button-width);
}

.cluster-wrapper:not(.active-cluster) .cluster-item-close:hover {
  background-color: #e6e6e6;
}

.cluster-wrapper:not(.active-cluster) .cluster-item-close:active {
  background: #d4d4d4;
  box-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125);
}

.icons {
  display: flex;
  align-items: center;
}

.icons * {
  margin-right: 0.2rem;
}

.icons .fa-exclamation-triangle {
  margin-left: 0.2rem;
  color: var(--bs-warning);
}
</style>
