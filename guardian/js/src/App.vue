<template>
  <AppHeader class="shared-app-header" />
</template>

<script setup>
import { useStore } from "vuex";
import AppHeader from "$shared/components/AppHeader.vue";
import { initializeSharedStores } from "$shared";

const store = useStore();

(async () => {
  initializeSharedStores(store);
})();
</script>

<style scoped>
.shared-app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1030;
}
</style>
