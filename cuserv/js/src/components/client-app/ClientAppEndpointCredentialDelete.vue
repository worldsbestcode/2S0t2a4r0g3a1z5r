<template>
  <CuservModal title="Delete Endpoint Credential" text="Delete">
    <template #content="{ toggleModal }">
      <ModalDeleteBody
        axios-emit="updateEndpoint"
        error="Failed to delete credential"
        success="Credential deleted"
        :url="`/cuserv/v1/clientapp/endpoint/${props.endpointUuid}/${props.credentialUuid}`"
        @cancel="toggleModal"
        @finished="toggleModal"
      />
    </template>
  </CuservModal>
</template>

<script setup>
import { defineProps } from "vue";

import CuservModal from "@/components/CuservModal.vue";
import ModalDeleteBody from "@/components/ModalDeleteBody.vue";

const props = defineProps({
  endpointUuid: {
    type: String,
    required: true,
  },
  credentialUuid: {
    type: String,
    required: true,
  },
});
</script>
