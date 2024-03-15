<template>
  <ModalDeleteBody
    axios-emit="updateCryptospaces"
    error="Failed to delete key slot"
    success="Key Slot deleted"
    :url="`/dki/v1/keyslots/${props.keySlotUuid}`"
    @finished="emit('refreshContent')"
  />
</template>

<script setup>
import { defineEmits, defineProps } from "vue";

import ModalDeleteBody from "@/components/ModalDeleteBody.vue";

const emit = defineEmits(["refreshContent"]);
const props = defineProps({
  keySlotUuid: {
    type: String,
    required: true,
  },
});
</script>
