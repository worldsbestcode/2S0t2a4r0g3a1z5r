<template>
  <ChcLabel div v-bind="props">
    <ChcToggleSwitch v-model="modelValue" :small="props.small" />
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcToggleSwitch from "$shared/components/ChcToggleSwitch.vue";
import { chcLabel } from "$shared/props.js";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  ...chcLabel,
  modelValue: {
    type: Boolean,
  },
  small: {
    type: Boolean,
  },
});

const modelValue = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});
</script>
