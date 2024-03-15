<template>
  <div class="modal-button-bottom">
    <!-- type="button" is probably for form support -->
    <ChcButton type="button" secondary @click="emit('cancel')">
      CANCEL
    </ChcButton>

    <ChcButton :loading="props.loading" @click="emit('action')">
      {{ props.text }}
    </ChcButton>
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";

const emit = defineEmits(["action", "cancel"]);

const props = defineProps({
  text: {
    type: String,
    required: true,
  },
  loading: {
    type: Boolean,
  },
});
</script>

<style scoped>
.modal-button-bottom {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  justify-content: space-between;
}
</style>
