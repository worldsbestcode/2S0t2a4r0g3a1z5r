<template>
  <WizardPage title="Perfect, service is deployed and ready to use!">
    <WizardFinishAnimation />

    <div class="finished-buttons">
      <!-- todo: Find a way to open the add new modals for these links -->

      <RouterLink
        replace
        :to="{
          name: 'deployedService',
          params: {
            serviceUuid: props.serviceUuid,
          },
        }"
        class="button-secondary button-link"
      >
        Manage Service
      </RouterLink>

      <RouterLink
        v-if="actionLink"
        replace
        :to="actionLink.to"
        class="button-primary button-link"
      >
        {{ actionLink.text }}
      </RouterLink>
    </div>
  </WizardPage>
</template>

<script setup>
import { computed, defineProps, inject } from "vue";

import WizardPage from "$shared/components/wizard/WizardPage.vue";

import WizardFinishAnimation from "@/components/wizard/WizardFinishAnimation.vue";

const templateData = inject("templateData");

const props = defineProps({
  serviceUuid: {
    type: String,
    required: true,
  },
});

const actionLinks = {
  GoogleEkms: {
    text: "Create CryptoSpace",
    to: {
      name: "cryptospaces",
      params: {
        serviceUuid: props.serviceUuid,
      },
    },
  },
  ClientApplication: {
    text: "Deploy Client Endpoint",
    to: {
      name: "endpoints",
      params: {
        serviceUuid: props.serviceUuid,
      },
    },
  },
  GoogleCse: {
    text: "Create User",
    to: {
      name: "googleUsers",
      params: {
        serviceUuid: props.serviceUuid,
      },
    },
  },
};

const actionLink = computed(
  () => actionLinks[templateData.value?.params?.type],
);
</script>
