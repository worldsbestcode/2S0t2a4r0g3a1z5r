<template>
  <ChcLabel div label="Injection Mode">
    <div class="radio-container">
      <ChcRadio
        v-model="injectionMode"
        type="radio"
        value="Legacy"
        label="Inject using legacy command"
      />
      <ChcRadio
        v-model="injectionMode"
        type="radio"
        value="ClearKey"
        label="Inject keys in the clear"
      />
      <ChcRadio
        v-model="injectionMode"
        type="radio"
        value="ClearKTK"
        label="Inject keys with clear KTK"
      />
      <ChcRadio
        v-model="injectionMode"
        type="radio"
        value="UnderKTK"
        label="Inject keys under preloaded KTK"
      />
    </div>
  </ChcLabel>

  <ChcLabel div label="Injection Settings">
    <ChcToggle
      v-model:modelValue="errors"
      small
      side="right"
      label="Show error code descriptions"
    />
    <ChcToggle
      v-model:modelValue="deleteKeys"
      small
      side="right"
      label="Delete keys before injection"
    />
    <ChcToggle
      v-if="injectionMode !== 'Legacy'"
      v-model:modelValue="version2"
      small
      side="right"
      label="Always use injection format 2"
    />
    <ChcToggle
      v-if="displayKTKOptions"
      v-model:modelValue="tr31Mode"
      small
      side="right"
      label="Send as TR-31 keyblock"
    />
    <div class="dki-combobox">
      <ChcComboBox
        v-if="displayKTKOptions"
        v-model:modelValue="bindingMethod"
        :values="bindingValues"
        label="TDES key block binding method"
      />
    </div>
    <ChcSpinner
      v-if="displayKTKOptions"
      v-model:modelValue="ktkSlot"
      min="0"
      max="255"
      step="1"
      label="Encrypting KTK slot"
    />
    <ChcComboBox
      v-if="displayKTKOptions"
      v-model:modelValue="ktkKeyType"
      class="dki-combobox"
      :values="ktkValues"
      label="Encryption KTK type"
    />
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcRadio from "$shared/components/ChcRadio.vue";
import ChcSpinner from "$shared/components/ChcSpinner.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";

const emit = defineEmits(["update:options"]);
const props = defineProps({
  options: {
    type: Object,
    required: true,
  },
});

const bindingValues = [
  {
    label: "Version A",
    value: "VersionA",
  },
  {
    label: "Version B",
    value: "VersionB",
  },
  {
    label: "Version C",
    value: "VersionC",
  },
];

const ktkValues = [
  {
    label: "Key Transfer Key",
    value: "KeyTransferKey",
  },
  {
    label: "Default KTK",
    value: "DefaultKTK",
  },
];

const injectionMode = computed({
  get() {
    return props.options.injectionScheme;
  },

  set(value) {
    let options = props.options;
    options.injectionScheme = value;
    emit("update:options", options);
  },
});

const ktkSlot = computed({
  get() {
    return props.options.ktkSlot;
  },

  set(value) {
    let options = props.options;
    options.ktkSlot = value;
    emit("update:options", options);
  },
});

const deleteKeys = computed({
  get() {
    return props.options.deleteKeys;
  },

  set(value) {
    let options = props.options;
    options.deleteKeys = value;
    emit("update:options", options);
  },
});

const version2 = computed({
  get() {
    return props.options.version2;
  },

  set(value) {
    let options = props.options;
    options.version2 = value;
    emit("update:options", options);
  },
});

const tr31Mode = computed({
  get() {
    return props.options.tr31Mode;
  },

  set(value) {
    let options = props.options;
    options.tr31Mode = value;
    emit("update:options", options);
  },
});

const ktkKeyType = computed({
  get() {
    return props.options.ktkKeyType;
  },

  set(value) {
    let options = props.options;
    options.ktkKeyType = value;
    emit("update:options", options);
  },
});

const bindingMethod = computed({
  get() {
    return props.options.bindingMethod;
  },

  set(value) {
    let options = props.options;
    options.bindingMethod = value;
    emit("update:options", options);
  },
});

const errors = computed({
  get() {
    return props.options.errors;
  },

  set(value) {
    let options = props.options;
    options.errors = value;
    emit("update:options", options);
  },
});

const displayKTKOptions = computed(() => {
  return (
    injectionMode.value === "ClearKTK" || injectionMode.value === "UnderKTK"
  );
});
</script>

<style scoped>
.dki-combobox {
  margin-top: 2rem;
  width: 400px;
}
</style>
