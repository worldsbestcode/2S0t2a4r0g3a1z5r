<template>
  <CuservModal title="Delete CSE User" v-bind="modalProps">
    <template #content="{ toggleModal }">
      <GoogleUserDeleteBody
        v-bind="$attrs"
        @finished="toggleModal"
        @cancel="toggleModal"
      />
    </template>
  </CuservModal>
</template>

<script setup>
import { defineProps } from "vue";

import CuservModal from "@/components/CuservModal.vue";
import GoogleUserDeleteBody from "@/components/google-user/GoogleUserDeleteBody.vue";
import { defineModalProps, useDeleteModalProps } from "@/misc.js";

const props = defineProps(defineModalProps);
const modalProps = useDeleteModalProps(props);
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
