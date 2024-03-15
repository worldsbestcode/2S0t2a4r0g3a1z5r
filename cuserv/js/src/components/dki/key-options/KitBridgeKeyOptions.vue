<template>
  <div>
    <ChcComboBox
      v-model:modelValue="keyType"
      label="Key Type:"
      :values="getKeyTypeOptions()"
    />
    <ChcComboBox
      v-if="state.displayKeyPurpose"
      v-model:modelValue="keyPurpose"
      label="Key Purpose:"
      :values="keyPurposeOptions"
    />
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import { eKeyType } from "$shared/utils/keys.js";

const emit = defineEmits(["update:options"]);
const props = defineProps({
  options: {
    type: Object,
    required: true,
  },
  keyType: {
    number: Number,
    required: true,
  },
});

const keyType = computed({
  get() {
    return props.options.keyType;
  },
  set(value) {
    let options = props.options;
    options.keyType = value;
    emit("update:options", options);
  },
});

const keyPurpose = computed({
  get() {
    return props.options.keyPurpose;
  },
  set(value) {
    let options = props.options;
    options.keyPurpose = value;
    emit("update:options", options);
  },
});
const state = {
  displayKeyPurpose: false,
};

const eKeyTypes = Object.freeze({
  eTerminal: "Terminal",
  eMaster: "Master",
  eSession: "Session",
  ePinEncryption: "PinEncryption",
  eDataEcnryption: "DataEncryption",
  eE2EE: "E2EE",
  eOnGaurdSde: "OnGaurdSde",
  eHMAC: "HMac",
});

const eKeyPurpose = Object.freeze({
  eMSPinEncryption: "MSPinEncryption",
  eMAC: "MAC",
  eComm: "Comm",
});

const dukptTypeOptions = [
  {
    value: eKeyTypes.ePinEncryption,
    label: "'D' - Pin Encryption",
  },
  {
    value: eKeyTypes.eDataEcnryption,
    label: "'d' - Data Encryption",
  },
  {
    value: eKeyTypes.eE2EE,
    label: "'e' - E2EE DUKPT",
  },
  {
    value: eKeyTypes.eOnGaurdSde,
    label: "'D' - OnGaurd SDE DUKPT",
  },
];

const masterTypeOptions = [
  {
    value: eKeyTypes.eTerminal,
    label: "'T' - Terminal base special key",
  },
  {
    value: eKeyTypes.eMaster,
    label: "'M' - Master Key",
  },
  {
    value: eKeyTypes.eSession,
    label: "'S' - Session Key",
  },
];

const macTypeOptions = [
  {
    value: eKeyTypes.eHMAC,
    label: "'H' - Terminal based special key",
  },
];

const keyPurposeOptions = [
  {
    value: eKeyPurpose.eMSPinEncryption,
    label: "'P' - Pin Encryption",
  },
  {
    value: eKeyPurpose.eComm,
    label: "'C' - Communictaion",
  },
  {
    value: eKeyPurpose.eMAC,
    label: "'M' - Mac Calculation and Verification",
  },
];

function isDukpt(keyType) {
  if (
    keyType === eKeyType.eAesDukptBdk ||
    keyType === eKeyType.eAesDukptInitial ||
    keyType === eKeyType.eDukptBdkKey ||
    keyType === eKeyType.eDukpt3DesBdkKey ||
    keyType === eKeyType.eDukptInitialKey
  ) {
    return true;
  }

  return false;
}

function getKeyTypeOptions() {
  let keyOptions = [];
  if (isDukpt(props.keyType)) {
    keyOptions = dukptTypeOptions;
    state.displayKeyPurpose = false;
  } else if (
    props.keyType === eKeyType.eMasterSession ||
    props.keyType === eKeyType.ePinEncryptionKey ||
    props.keyType === eKeyType.eGenericBdk
  ) {
    keyOptions = masterTypeOptions;
    state.displayKeyPurpose = true;
  } else if (props.keyType === eKeyType.eMacKey) {
    keyOptions = macTypeOptions;
    state.displayKeyPurpose = false;
  }

  return keyOptions;
}
</script>
