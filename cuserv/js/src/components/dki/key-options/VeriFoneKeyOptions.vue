<template>
  <div>
    <ChcComboBox
      v-model:modelValue="keyUsage"
      label="Key Usage:"
      :values="keyUsageOptions"
    />
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcComboBox from "$shared/components/ChcComboBox.vue";

const emit = defineEmits(["update:options"]);
const props = defineProps({
  options: {
    type: Object,
    required: true,
  },
});

const eKeyUsage = Object.freeze({
  eKeyEncryption: "KeyEncryption",
  ePinEncryption: "PinEncryption",
  eMacAlgo0: "MacAlgo0",
  eMacAlgo1: "MacAlgo1",
  eMacAlgo2: "MacAlgo2",
  eMacAlgo3: "MacAlgo3",
  eMacAlgo4: "MacAlgo4",
  eMacAlgo5: "MacAlgo5",
  eMacAlgo6: "MacAlgo6",
});
const keyUsage = computed({
  get() {
    return props.options.keyUsage;
  },
  set(value) {
    let options = props.options;
    options.keyUsage = value;
    emit("update:options", options);
  },
});

const keyUsageOptions = [
  {
    value: eKeyUsage.eKeyEncryption,
    label: "K0 - Key Encryption",
  },
  {
    value: eKeyUsage.ePinEncryption,
    label: "P0 - Pin Encryption",
  },
  {
    value: eKeyUsage.eMacAlgo0,
    label: "00 - Mac Algo 1 (56 bits)",
  },
  {
    value: eKeyUsage.eMacAlgo1,
    label: "10 - Mac Algo 1 (112 bits)",
  },
  {
    value: eKeyUsage.eMacAlgo2,
    label: "20 - Mac Algo 2",
  },
  {
    value: eKeyUsage.eMacAlgo3,
    label: "30 - Mac Algo 3",
  },
  {
    value: eKeyUsage.eMacAlgo4,
    label: "40 - Mac Algo 4",
  },
  {
    value: eKeyUsage.eMacAlgo5,
    label: "50 - Mac Algo 5 (56 bits)",
  },
  {
    value: eKeyUsage.eMacAlgo6,
    label: "60 - Mac Algo 5 (112 bits)",
  },
];
</script>
