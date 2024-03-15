<template>
  <button class="information-and-actions-show">
    {{ props.show ? "Hide" : "Show" }}
    <span class="material-symbols-outlined information-and-actions-show__icon">
      expand_{{ props.show ? "less" : "more" }}
    </span>
  </button>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  show: {
    type: Boolean,
  },
});
</script>

<style scoped>
.information-and-actions-show {
  border: 0;
  background: 0;
  color: var(--muted-text-color);

  display: inline-flex;
  align-items: center;
}

.information-and-actions-show__icon {
  color: var(--primary-text-color);
}
</style>
