<template>
  <ModalDeleteBody
    axios-emit="updateServiceAccounts"
    error="Failed to delete Google Cloud service account"
    success="Google Cloud service account deleted"
    :url="`/gekms/v1/accounts/${props.serviceUuid}/${props.serviceAccountName}`"
  />
</template>

<script setup>
import { defineProps } from "vue";

import ModalDeleteBody from "@/components/ModalDeleteBody.vue";

const props = defineProps({
  serviceUuid: {
    type: String,
    required: true,
  },
  serviceAccountName: {
    type: String,
    required: true,
  },
});
</script>
