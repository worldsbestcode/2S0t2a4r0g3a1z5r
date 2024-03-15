<template>
  <div class="cover-screen">
    <RouterBreadCrumbs :crumbs="crumbs" />

    <component :is="componentToRender" />
  </div>
</template>

<script setup>
import { computed, defineProps } from "vue";
import { useRoute } from "vue-router";

import RouterBreadCrumbs from "$shared/components/RouterBreadCrumbs.vue";

import WizardDeployClientApp from "@/components/wizard/WizardDeployClientApp.vue";
import WizardDeployGoogleCse from "@/components/wizard/WizardDeployGoogleCse.vue";
import WizardDeployGoogleEkms from "@/components/wizard/WizardDeployGoogleEkms.vue";
import WizardDeployPedInject from "@/components/wizard/WizardDeployPedInject.vue";

const route = useRoute();

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
  templateType: {
    type: String,
    default: "",
  },
});

const componentToRender = computed(() => {
  switch (props.templateType) {
    case "ClientApplication":
      return WizardDeployClientApp;
    case "GoogleCse":
      return WizardDeployGoogleCse;
    case "GoogleEkms":
      return WizardDeployGoogleEkms;
    case "PedInjection":
      return WizardDeployPedInject;
    default:
      return null;
  }
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "deploy",
        params: route.params,
      },
      name: "Deploy",
    },
  ];
});
</script>
