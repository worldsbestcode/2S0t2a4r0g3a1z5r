<template>
  <button :class="props.active && 'active-category'" class="category-button">
    <h3>
      <slot />
    </h3>
    <span class="material-symbols-outlined category-arrow-icon">
      arrow_forward
    </span>
  </button>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  active: {
    type: Boolean,
    default: false,
  },
});
</script>
