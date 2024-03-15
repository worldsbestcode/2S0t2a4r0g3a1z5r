<template>
  <!-- todo: Add title to the button -->
  <button
    :class="[
      props.small && 'button-small',
      props.secondary ? 'button-secondary' : 'button-primary',
    ]"
    :disabled="disabled"
  >
    <LoadingSpinner :loading="props.loading" />
    <img v-if="props.img" class="chc-button-img" :src="props.img" />
    <div class="button-inner-wrapper">
      <slot />
    </div>
  </button>
</template>

<script setup>
import { computed, defineProps } from "vue";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

const props = defineProps({
  img: {
    type: String,
    default: undefined,
  },
  loading: {
    type: Boolean,
  },
  disabled: {
    type: Boolean,
  },
  secondary: {
    type: Boolean,
  },
  small: {
    type: Boolean,
  },
});

const disabled = computed(() => {
  if (props.loading) {
    return true;
  } else {
    return props.disabled;
  }
});
</script>
