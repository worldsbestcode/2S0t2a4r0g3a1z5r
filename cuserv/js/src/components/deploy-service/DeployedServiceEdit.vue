<template>
  <CuservModal title="Edit Service" icon="pencil">
    <template #content="{ toggleModal }">
      <DeployedServiceEditBody
        v-bind="$attrs"
        @cancel="toggleModal"
        @finished="toggleModal"
      />
    </template>
  </CuservModal>
</template>

<script setup>
import CuservModal from "@/components/CuservModal.vue";
import DeployedServiceEditBody from "@/components/deploy-service/DeployedServiceEditBody.vue";
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
