<template>
  <ChcLabel div v-bind="props">
    <select v-model="modelValue" class="chc-input">
      <slot />
    </select>
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcLabel from "$shared/components/ChcLabel.vue";
import { chcLabel } from "$shared/props.js";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  ...chcLabel,
  modelValue: {
    type: null,
    required: true,
  },
});

const modelValue = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});
</script>
