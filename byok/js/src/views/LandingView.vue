<template>
  <div class="main-canvas">
    <div class="management-page landing-page">
      <header class="landing-page-header">
        <p class="landing-page-header-text">HSM Cluster Management</p>
      </header>
      <main class="landing-page-main">
        <div v-if="clusters && clusters.length > 0">
          <p>Choose an HSM cluster</p>
          <nav class="landing-page-nav">
            <router-link
              v-for="cluster in clusters"
              :key="cluster.id"
              class="button cluster-option"
              :to="{
                name: cluster.session.loginComplete ? 'actions' : 'login',
                params: { clusterId: cluster.id },
              }"
            >
              {{ cluster.name }}
            </router-link>
          </nav>
        </div>
        <p v-else class="m-0">No available HSM clusters</p>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    clusters: function () {
      return this.$store.state.byok.clusters;
    },
  },
};
</script>

<style scoped>
.landing-page {
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.landing-page-header {
  padding: 0.5rem;
}

.landing-page-header-text {
  text-align: center;
}

.landing-page-main {
  padding: 1rem;
  text-align: center;
}

.landing-page-nav {
  display: grid;
  grid-template-columns: repeat(auto-fit, var(--box-width));
  gap: 0.5rem;
}

.cluster-option {
  padding: 0.5rem;
  color: var(--text-color);
  text-decoration: none;
}
</style>
