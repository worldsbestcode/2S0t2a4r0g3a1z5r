<template>
  <input
    :id="$.uid.toString()"
    v-model="modelValue"
    :type="props.type"
    :value="props.value"
    class="chc-radio__input"
    :disabled="props.disabled"
  />
  <label
    :for="$.uid.toString()"
    class="chc-radio"
    :class="props.noContainer && 'chc-radio--no-container'"
  >
    <div class="fake-checkbox">
      <div class="fake-checkbox__body" />
    </div>
    <div v-if="props.label" :title="props.label" class="chc-radio__label">
      {{ props.label }}
    </div>
  </label>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: {
    type: undefined,
    required: true,
  },
  type: {
    type: String,
    default: "radio",
  },
  value: {
    type: undefined,
    default: undefined,
  },
  label: {
    type: String,
    default: undefined,
  },
  disabled: {
    type: Boolean,
  },
  noContainer: {
    type: Boolean,
  },
});

const modelValue = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});
</script>

<style scoped>
.chc-radio__input {
  display: none;
  cursor: pointer;
}

.chc-radio__label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chc-radio {
  border-radius: 5px;
  border: 1px solid var(--border-color);
  padding: 1rem;
  background: var(--primary-background-color);

  display: flex;
  align-items: center;
  gap: 0.5rem;

  cursor: pointer;
}

.chc-radio:hover {
  border-color: #cf9d9c;
  background: var(--secondary-background-color);
}

.chc-radio__input:checked + .chc-radio {
  border-color: var(--primary-color);
  background: #e8e6e6;
  font-weight: 500;
}

.chc-radio__input:disabled + .chc-radio {
  background: var(--primary-background-color);
  color: var(--muted-text-color);
  pointer-events: none;
}

.chc-radio__input[type="radio"] + .chc-radio .fake-checkbox {
  border-radius: 50%;
}

.fake-checkbox {
  flex-shrink: 0;
  padding: 2px;
  width: 1.2rem;
  height: 1.2rem;
  border: 2px solid var(--border-color);
  background: var(--primary-background-color);
}

.chc-radio__input:checked + .chc-radio .fake-checkbox {
  border-color: var(--primary-color);
}

.chc-radio:hover .fake-checkbox {
  border-color: #cf9d9c;
}

.chc-radio__input[type="radio"] + .chc-radio .fake-checkbox__body {
  border-radius: 50%;
}

.fake-checkbox__body {
  display: none;
  height: 100%;
  width: 100%;
  background: var(--primary-color);
}
.chc-radio__input:checked + .chc-radio .fake-checkbox .fake-checkbox__body {
  display: block;
}

.chc-radio--no-container {
  background: 0 !important;
  border: 0 !important;
  padding: 0;
  display: inline-flex;
}
</style>
