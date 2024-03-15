<template>
  <AppHeader class="regauth-app-header" />
</template>

<script setup>
import { useStore } from "vuex";
import AppHeader from "$shared/components/AppHeader.vue";
import { initializeSharedStores } from "$shared";

const store = useStore();

(async () => {
  await initializeSharedStores(store);
})();
</script>
