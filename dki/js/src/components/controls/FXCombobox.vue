<template>
  <div class="fx-combobox-container">
    <fx-label class="mr-2" :text="text" theme="primary" />
    <select v-model="input" class="fx-combobox">
      <option v-for="opt in options" :key="opt">
        {{ opt }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits } from "vue";

const emit = defineEmits(["update:input"]);
const props = defineProps({
  input: {
    type: String,
    required: true,
  },
  options: {
    type: Array,
    required: true,
  },
  text: {
    type: String,
    requried: true,
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
.fx-combobox-container {
  display: flex;
  align-items: center;
}
.fx-combobox {
  appearance: menulist;
  border: 1px solid var(--border-color);
  border-radius: 5px;
  height: 40px;
  min-width: fit-content;
  padding: 0 0.5rem;
}
</style>
