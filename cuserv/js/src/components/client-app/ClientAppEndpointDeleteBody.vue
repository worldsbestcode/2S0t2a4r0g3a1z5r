<template>
  <ModalDeleteBody
    axios-emit="updateEndpoints"
    error="Failed to delete endpoint"
    success="Endpoint deleted"
    :url="`/cuserv/v1/clientapp/endpoint/${props.endpointUuid}`"
  />
</template>

<script setup>
import { defineProps } from "vue";

import ModalDeleteBody from "@/components/ModalDeleteBody.vue";

const props = defineProps({
  endpointUuid: {
    type: String,
    required: true,
  },
});
</script>
