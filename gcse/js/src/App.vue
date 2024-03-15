<template>
  <div class="app">
    <AppHeader />

    <router-view />
  </div>
</template>

<script setup>
import AppHeader from "$shared/components/AppHeader.vue";
</script>

<style scoped>
.app {
  height: 100vh;
  display: grid;
  grid-template-rows: max-content 1fr;

  font-family: "Roboto", sans-serif;
}
</style>
