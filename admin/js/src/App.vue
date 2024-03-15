<template>
  <AppHeader />
  <RouterView />
</template>

<script setup>
import AppHeader from "$shared/components/AppHeader.vue";
</script>

<style>
.wizard-page-title {
  color: var(--primary-color);
}
</style>
