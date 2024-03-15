<template>
  <label class="chc-label">
    <span class="chc-label__text">
      {{ props.label
      }}<span v-if="props.hint" class="chc-label__hint">{{ props.hint }} </span>
    </span>
    <select
      v-bind="$attrs"
      v-model="modelValue"
      style="flex-grow: 1"
      class="chc-input"
    >
      <option
        v-for="value in props.values"
        :key="value.value"
        :value="value.value"
        :selected="value.value == props.modelValue"
      >
        {{ value.label }}
      </option>
    </select>
  </label>
</template>

<script setup>
import { computed, defineEmits, defineProps, onMounted } from "vue";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  values: {
    type: Array,
    required: true,
  },
  hint: {
    type: String,
    default: undefined,
  },
  label: {
    type: String,
    required: true,
  },
});

const modelValue = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit("update:modelValue", value);
  },
});

onMounted(() => {
  if (!modelValue.value && props.values.length > 0) {
    modelValue.value = props.values[0].value;
  }
});
</script>
