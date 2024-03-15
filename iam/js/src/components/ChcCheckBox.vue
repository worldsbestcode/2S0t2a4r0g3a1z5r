<template>
  <ChcLabel v-bind="props">
    <input
      v-bind="$attrs"
      style="flex-grow: 1"
      type="checkbox"
      :checked="props.modelValue"
      @change="emit('update:modelValue', !props.modelValue)"
    />
  </ChcLabel>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";

import ChcLabel from "$shared/components/ChcLabel.vue";
import { chcLabel } from "$shared/props.js";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  ...chcLabel,
  modelValue: {
    type: Boolean,
    required: true,
  },
});
</script>
