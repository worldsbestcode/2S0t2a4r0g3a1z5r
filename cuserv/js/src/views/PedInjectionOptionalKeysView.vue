<template>
  <div
    class="cover-screen"
    style="background: var(--secondary-background-color)"
  >
    <DeployedServiceHeader :crumbs="crumbs" />
    <DKIServiceSelectWizard
      :service-uuid="props.serviceUuid"
      :service-name="props.serviceName"
    />
  </div>
</template>

<script setup>
import { computed, defineProps } from "vue";
import { useRoute } from "vue-router";

import DeployedServiceHeader from "@/components/deploy-service/DeployedServiceHeader.vue";
import DKIServiceSelectWizard from "@/components/dki/DKIServiceSelectWizard.vue";

const route = useRoute();

const props = defineProps({
  serviceName: {
    type: String,
    required: true,
  },
  crumbs: {
    type: Array,
    required: true,
  },
  serviceUuid: {
    type: String,
    required: true,
  },
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: { name: "pedinjectServices", params: route.params },
      name: "Select Optional Keys",
    },
  ];
});
</script>
