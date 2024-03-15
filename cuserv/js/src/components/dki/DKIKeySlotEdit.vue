<template>
  <ModalAddNew
    :body="DKIKeySlotEditBody"
    title="Create Key Slot"
    @finished="emit('finished')"
  />
</template>

<script setup>
import { defineEmits } from "vue";

import DKIKeySlotEditBody from "@/components/dki/DKIKeySlotEditBody.vue";
import ModalAddNew from "@/components/ModalAddNew.vue";

const emit = defineEmits(["finished"]);
</script>
