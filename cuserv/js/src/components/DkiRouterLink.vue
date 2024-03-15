<template>
  <ChcMainRouterLink
    v-if="pedInjectionServiceFound"
    :to="{ name: 'pedinjectServices' }"
  >
    Key Injection Wizard
  </ChcMainRouterLink>
</template>

<script setup>
import { computed } from "vue";

import ChcMainRouterLink from "$shared/components/ChcMainRouterLink.vue";

import { useDeployedServicesStore } from "@/store/deployed-services";

const deployedServicesStore = useDeployedServicesStore();

const pedInjectionServiceFound = computed(() =>
  deployedServicesStore.services.some((x) => x.type === "PedInjection"),
);
</script>
