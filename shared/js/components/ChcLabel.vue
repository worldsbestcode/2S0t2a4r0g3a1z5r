<template>
  <component
    :is="props.div ? 'div' : 'label'"
    class="chc-label"
    :class="props.side && 'side-label'"
  >
    <template v-if="props.side === 'right'">
      <slot />
    </template>
    <span class="chc-label__text" :style="textStyle">
      {{ props.label
      }}<span v-if="props.hint" class="chc-label__hint">{{ props.hint }} </span>
    </span>
    <template v-if="props.side === 'left' || props.side === undefined">
      <slot />
    </template>
    <div v-if="props.error" class="chc-label__error">{{ props.error }}</div>
  </component>
</template>

<script setup>
import { computed, defineProps } from "vue";

import { chcLabel } from "$shared/props.js";

// Add div support mainly to stop Firefox from spamming: Empty string passed to getElementById()

const props = defineProps({
  ...chcLabel,
  div: {
    type: Boolean,
  },
  center: {
    type: Boolean,
  },
  error: {
    type: String,
    default: undefined,
  },
});

const textStyle = computed(() => {
  const style = {};
  if (props.side) {
    style.display = "inline";
  }
  if (props.center) {
    style.textAlign = "center";
  }
  return style;
});
</script>

<style scoped>
.side-label {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chc-label__error {
  margin-top: 0.2rem;
  color: var(--primary-color);
  width: 480px;
}
</style>
