<template>
  <CuservModal title="Delete Service" icon="trash">
    <template #content="{ toggleModal }">
      <DeployedServiceDeleteBody
        :uuid="props.uuid"
        @cancel="toggleModal"
        @finished="
          toggleModal();
          $emit('finished');
        "
      />
    </template>
  </CuservModal>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";

import CuservModal from "@/components/CuservModal.vue";
import DeployedServiceDeleteBody from "@/components/deploy-service/DeployedServiceDeleteBody.vue";

defineEmits(["finished"]);
const props = defineProps({
  uuid: {
    type: String,
    required: true,
  },
});
</script>
