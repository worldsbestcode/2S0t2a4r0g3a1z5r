<template>
  <div class="wizard-page-container">
    <div class="wizard-page-name">
      <LoadingSpinner
        style="display: inline-block; margin: 0"
        :loading="props.loading"
      />

      <span class="wizard-page-title">
        {{ props.title }}
      </span>

      <span v-if="props.hint" class="chc-label__hint">
        {{ props.hint }}
      </span>
    </div>

    <div class="wizard-page-description">
      {{ props.description }}
    </div>

    <slot />
  </div>
</template>

<script setup>
import { defineProps } from "vue";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

const props = defineProps({
  loading: {
    type: Boolean,
  },
  title: {
    type: String,
    required: true,
  },
  hint: {
    type: String,
    default: undefined,
  },
  description: {
    type: String,
    default: undefined,
  },
});
</script>
