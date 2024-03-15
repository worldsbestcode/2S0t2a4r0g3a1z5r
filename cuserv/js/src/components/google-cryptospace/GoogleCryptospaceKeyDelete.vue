<template>
  <CuservModal title="Delete Key" v-bind="modalProps">
    <template #content="{ toggleModal }">
      <GoogleCryptospaceKeyDeleteBody
        v-bind="$attrs"
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
import GoogleCryptospaceKeyDeleteBody from "@/components/google-cryptospace/GoogleCryptospaceKeyDeleteBody.vue";
import { defineModalProps, useDeleteModalProps } from "@/misc.js";

defineEmits(["finished"]);
const props = defineProps(defineModalProps);
const modalProps = useDeleteModalProps(props);
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
