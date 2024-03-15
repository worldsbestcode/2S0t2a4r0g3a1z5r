<template>
  <div
    class="cover-screen"
    style="background: var(--secondary-background-color)"
  >
    <DeployedServiceHeader :crumbs="props.crumbs" />

    <div style="padding: 0 2rem; margin: 1rem 0">
      <div style="max-width: 80rem; margin: auto">
        <LoadingSpinner :loading="props.loading" />
      </div>
    </div>

    <slot />
  </div>

  <slot name="routerView">
    <RouterView :crumbs="props.crumbs" />
  </slot>
</template>

<script setup>
import { defineProps } from "vue";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

import DeployedServiceHeader from "@/components/deploy-service/DeployedServiceHeader.vue";

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    required: false,
  },
});
</script>
