<template>
  <ChcInput
    v-model="name"
    hint="length 3-128"
    label="Name"
    placeholder="Key name"
  />

  <ChcLabel v-if="keyAlgorithm" div label="Key Algorithm">
    <div class="radio-container radio-container--two-col">
      <ChcRadio
        v-for="algorithm in keyAlgorithms"
        :key="algorithm"
        v-model="keyAlgorithm"
        type="radio"
        :value="algorithm"
        :label="algorithm"
      />
    </div>
  </ChcLabel>

  <ChcLabel div label="Justification">
    <div class="radio-container radio-container--two-col">
      <ChcRadio
        v-for="justification in googleJustifications"
        :key="justification"
        v-model="justifications"
        type="checkbox"
        :label="justification"
        :value="justification"
      />
    </div>
  </ChcLabel>

  <ChcLabel v-if="props.rotationPeriod" div label="Rotation Period">
    <div class="joint-inputs">
      <input
        v-model="state.rotationNumber"
        style="flex-grow: 1"
        class="chc-input"
        type="number"
      />
      <select v-model="state.rotationUnit" class="chc-input">
        <option>Hours</option>
        <option>Days</option>
        <option>Months</option>
        <option>Years</option>
      </select>
    </div>
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps, reactive, watchEffect } from "vue";

import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcRadio from "$shared/components/ChcRadio.vue";

import {
  justifications as googleJustifications,
  keyAlgorithms,
} from "@/google.js";

const emit = defineEmits([
  "update:name",
  "update:keyAlgorithm",
  "update:justifications",
  "update:rotationPeriod",
]);

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  keyAlgorithm: {
    type: String,
    default: undefined,
  },
  justifications: {
    type: Array,
    required: true,
  },
  rotationPeriod: {
    type: String,
    required: true,
  },
});

const state = reactive({
  rotationNumber: props.rotationPeriod?.split(" ")[0],
  rotationUnit: props.rotationPeriod?.split(" ")[1],
});

const name = computed({
  get() {
    return props.name;
  },
  set(value) {
    emit("update:name", value);
  },
});
const keyAlgorithm = computed({
  get() {
    return props.keyAlgorithm;
  },
  set(value) {
    emit("update:keyAlgorithm", value);
  },
});
const justifications = computed({
  get() {
    return props.justifications;
  },
  set(value) {
    emit("update:justifications", value);
  },
});

watchEffect(() => {
  if (props.rotationPeriod) {
    emit(
      "update:rotationPeriod",
      `${state.rotationNumber} ${state.rotationUnit}`,
    );
  }
});
</script>

<style scoped>
.joint-inputs {
  display: flex;
  gap: 0.5rem;
}

.joint-inputs .chc-input {
  min-width: initial;
  width: initial;
}
</style>
