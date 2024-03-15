<template>
  <ChcLabel v-bind="props">
    <input
      class="chc-input"
      :value="props.modelValue"
      v-bind="$attrs"
      @input="handleInput($event)"
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
    type: [String, Number],
    required: true,
  },
  inputSanitize: {
    type: Object,
    required: false,
    default: undefined,
  },
});

function handleInput(event) {
  // Restrict using custom sanitization
  if (props.inputSanitize)
    event.target.value = props.inputSanitize(event.target.value);
  // Restrict common Excrypt formatting characters
  else event.target.value = event.target.value.replace(/[[\]<>#;,{}|]/g, "");

  emit("update:modelValue", event.target.value);
}
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
