<template>
  <div class="fx-text-field-container">
    <input
      v-model="input"
      class="chc-input fx-text-field"
      type="text"
      :placeholder="props.label"
    />
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

const emit = defineEmits(["update:input"]);
const props = defineProps({
  input: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: false,
    default: "",
  },
});

const input = computed({
  get() {
    return props.input;
  },
  set(value) {
    emit("update:input", value);
  },
});
</script>

<style scoped>
.fx-text-field-container {
  min-height: 30px;
  align-items: center;
}

.fx-text-field {
  border: 1px solid var(--border-color);
  max-width: 100%;
}
</style>
