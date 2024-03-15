<template>
  <CuservModal title="Edit Key" icon="pencil">
    <template #content="{ toggleModal }">
      <GoogleCryptospaceKeyEditBody
        v-bind="$attrs"
        @cancel="toggleModal"
        @finished="toggleModal"
      />
    </template>
  </CuservModal>
</template>

<script setup>
import CuservModal from "@/components/CuservModal.vue";
import GoogleCryptospaceKeyEditBody from "@/components/google-cryptospace/GoogleCryptospaceKeyEditBody.vue";
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
