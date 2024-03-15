<template>
  <CuservModal title="Delete CryptoSpace" v-bind="modalProps">
    <template #content="{ toggleModal }">
      <GoogleCryptospaceDeleteBody
        v-bind="$attrs"
        @cancel="toggleModal"
        @finished="toggleModal"
      />
    </template>
  </CuservModal>
</template>

<script setup>
import { defineProps } from "vue";

import CuservModal from "@/components/CuservModal.vue";
import GoogleCryptospaceDeleteBody from "@/components/google-cryptospace/GoogleCryptospaceDeleteBody.vue";
import { defineModalProps, useDeleteModalProps } from "@/misc.js";

const props = defineProps(defineModalProps);
const modalProps = useDeleteModalProps(props);
</script>
