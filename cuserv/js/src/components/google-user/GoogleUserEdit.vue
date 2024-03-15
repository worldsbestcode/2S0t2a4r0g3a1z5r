<template>
  <CuservModal title="Edit User" icon="pencil">
    <template #content="{ toggleModal }">
      <GoogleUserEditBody
        v-bind="$attrs"
        @finished="toggleModal"
        @cancel="toggleModal"
      />
    </template>
  </CuservModal>
</template>

<script setup>
import CuservModal from "@/components/CuservModal.vue";
import GoogleUserEditBody from "@/components/google-user/GoogleUserEditBody.vue";
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
