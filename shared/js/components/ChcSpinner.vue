<template>
  <label class="chc-label">
    <span class="chc-label__text">
      {{ title }}
      <span class="chc-label__hint">Min: {{ min }} - Max: {{ max }}</span>
    </span>
    <input
      v-model="number"
      class="chc-label__spinner"
      type="number"
      :step="step"
      :min="min"
      :max="max"
      @input="handleInput($event)"
    />
  </label>
</template>

<script setup>
import { computed, defineEmits, defineProps, onMounted } from "vue";

const emit = defineEmits(["update:modelValue"]);
const props = defineProps({
  modelValue: {
    type: Number,
    default: 0,
  },
  title: {
    type: String,
    default: "",
  },
  min: {
    type: Number,
    default: 0,
  },
  max: {
    type: Number,
    default: 10,
  },
  step: {
    type: Number,
    default: 0.5,
  },
});

const number = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    if (value !== "") {
      value = numbersOnly(String(value));
      emit("update:modelValue", value);
    }
  },
});

function clamp(value, max, min) {
  return Math.max(Math.min(value, max), min);
}

function numbersOnly(value) {
  let newValue = value.replace(/[^\d.]/g, "");
  newValue = clamp(value, props.max, props.min);
  return newValue;
}

function handleInput(event) {
  if (event.inputType === "insertText") {
    if (!event.target.value) {
      event.target.value = number.value;
    } else {
      let value = event.target.value;

      if ((value < props.min || value > props.max) && event.data !== ".") {
        // clamp
        event.target.value = clamp(value, props.max, props.min);
      }
    }
  }
}

onMounted(() => {
  number.value = clamp(number.value, props.max, props.min);
});
</script>

<style scoped>
.chc-label__spinner {
  display: block;
  height: 60px;
  padding: 0 20px;
  background: var(--primary-background-color);
  border: 1px solid var(--border-color);
  border-radius: 5px;
  color: var(--primary-text-color);
  outline: 0;
}
</style>
