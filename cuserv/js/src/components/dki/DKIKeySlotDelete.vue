<template>
  <CuservModal title="Delete Key Slot" v-bind="modalProps">
    <template #content="{ toggleModal }">
      <DKIKeySlotDeleteBody
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
import DKIKeySlotDeleteBody from "@/components/dki/DKIKeySlotDeleteBody.vue";
import { defineModalProps, useDeleteModalProps } from "@/misc.js";

const props = defineProps(defineModalProps);
const modalProps = useDeleteModalProps(props);
</script>
