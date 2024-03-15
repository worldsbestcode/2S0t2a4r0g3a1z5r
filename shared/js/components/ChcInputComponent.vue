<template>
  <ChcLabel v-bind="props">
    <textarea v-model="component" />
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
    type: String,
    required: true,
  },
});

const component = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit("update:modelValue", value);
  },
});
</script>
