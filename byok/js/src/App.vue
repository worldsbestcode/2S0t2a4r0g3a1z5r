<template>
  <app-header />

  <div v-if="loading" class="big-text-center">
    <loading-spinner class="init-loading-spinner" :loading="loading" />
  </div>

  <div v-if="initFailed" class="big-text-center main-canvas">
    <span>BYOK initialization failed</span>
    <button class="try-again button blue-button" @click="tryAgain">
      Try again
    </button>
  </div>
  <main-layout v-if="initComplete && !initFailed" />
</template>

<script>
import { useToast } from "vue-toastification";

import MainLayout from "@/layouts/MainLayout.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import AppHeader from "$shared/components/AppHeader.vue";
import { initializeSharedStores } from "$shared";

export default {
  name: "App",
  components: {
    MainLayout,
    LoadingSpinner,
    AppHeader,
  },
  setup: function () {
    return { toast: useToast() };
  },
  data: function () {
    return {
      initComplete: false,
      initFailed: false,
    };
  },
  computed: {
    loading: function () {
      return !this.initComplete && !this.initFailed;
    },
  },
  mounted: async function () {
    this.initializeVueToastr();
    await this.initializeStore();
    this.setRoute();

    this.initComplete = true;
  },
  methods: {
    initializeVueToastr: function () {
      this.$bus.on("toaster", ({ type, message }) => {
        if (type) {
          this.toast[type](message);
        } else {
          this.toast(message);
        }
      });
    },

    initializeStore: async function () {
      try {
        await this.$store.dispatch("byok/initializeClusters");
      } catch (error) {
        this.initFailed = true;
        return;
      }

      // We can addClusterDetails even if synchronizeClusterSessions fails
      try {
        await this.$store.dispatch("byok/synchronizeClusterSessions");
      } catch (error) {
        // synchronizeClusterSessions will toast errors...
      }

      // addClusterDetails should never throw an error
      await this.$store.dispatch("byok/addClusterDetails");

      await initializeSharedStores(this.$store);
    },

    tryAgain: function () {
      location.reload();
    },

    setRoute: function () {
      if (this.$route.name === "landing" || this.$route.name === "login") {
        return;
      }

      let clusterId = this.$route.params.clusterId;
      let currentCluster = this.$store.state.byok.clusters.find(
        (x) => x.id === clusterId,
      );
      if (currentCluster && !currentCluster.session.loginComplete) {
        this.$router.replace({ name: "login" });
      }
    },
  },
};
</script>

<style scoped>
.big-text-center {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2rem;
}

.init-loading-spinner {
  width: 5rem;
  height: 5rem;
  border-radius: 2.5rem;
}

.try-again {
  margin-left: 1rem;
  font-size: 1.5rem;
}
</style>
