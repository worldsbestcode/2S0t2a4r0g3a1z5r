<template>
  <CuservModal title="Edit CryptoSpace" icon="pencil">
    <template #content="{ toggleModal }">
      <GoogleCryptospaceEditBody
        v-bind="$attrs"
        @cancel="toggleModal"
        @finished="toggleModal"
      />
    </template>
  </CuservModal>
</template>

<script setup>
import CuservModal from "@/components/CuservModal.vue";
import GoogleCryptospaceEditBody from "@/components/google-cryptospace/GoogleCryptospaceEditBody.vue";
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
