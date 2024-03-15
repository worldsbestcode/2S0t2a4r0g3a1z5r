<template>
  <CuservModal title="Delete Google Cloud Service Account" text="Delete">
    <template #content="{ toggleModal }">
      <ServiceAccountDeleteBody
        v-bind="$attrs"
        @cancel="toggleModal"
        @finished="toggleModal"
      />
    </template>
  </CuservModal>
</template>

<script setup>
import CuservModal from "@/components/CuservModal.vue";
import ServiceAccountDeleteBody from "@/components/google/ServiceAccountDeleteBody.vue";
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
