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
      :values="getKeyPurposeOptions()"
    />

    <table class="deployed-manage-table">
      <thead>
        <tr>
          <th>Application ID</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="applicationIds.length === 0">
          <td :colspan="2" style="text-align: center">No Application IDs</td>
        </tr>
        <tr v-for="(id, index) in applicationIds" v-else :key="id">
          <td>{{ id }}</td>
          <td>
            <button
              class="deployed-manage-table__delete"
              @click="applicationIds.splice(index, 1)"
            >
              delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <Modal title="Add Application ID">
      <template #button="{ on }">
        <ChcButton
          class="dki-button"
          secondary
          small
          img="/shared/static/element-plus.svg"
          v-on="on"
        >
          Add Application ID
        </ChcButton>
      </template>
      <template #content="{ toggleModal }">
        <ChcSpinner
          v-model:modelValue="state.appId"
          title="App ID"
          min="0"
          step="1"
          max="300"
        />
        <ModalFooter
          text="Add"
          @action="
            () => {
              applicationIds.push(state.appId);
              toggleModal();
              state.appId = 0;
            }
          "
        />
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcSpinner from "$shared/components/ChcSpinner.vue";
import Modal from "$shared/components/Modal.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";
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

const applicationIds = computed({
  get() {
    return props.options.appIds;
  },
  set(value) {
    let options = props.options;
    options.appIds = value;
    emit("update:options", options);
  },
});

const state = {
  displayKeyPurpose: false,
  appId: 0,
};

const eKeyTypes = Object.freeze({
  eText: "Text",
  eTerminal: "Application",
  eMaster: "Master",
  eMasterUnderMaster: "MasterUnderMaster",
  eSession: "Session",
  ePinEncryption: "PinEncryption",
  eDataEcnryption: "DataEncryption",
  eE2EE: "E2EE",
  eOnGaurdSde: "OnGaurdSde",
});

const eKeyPurpose = Object.freeze({
  eMSPinEncryption: "MSPinEncryption",
  eMAC: "MAC",
  eComm: "Comm",
  eAtalla: "Atalla",
  eMother3DES: "Mother3DeS",
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
    label: "'f' - OnGaurd SDE DUKPT",
  },
];

const masterTypeOptions = [
  {
    value: eKeyTypes.eMaster,
    label: "'M' - Master Key",
  },
];

const pinEncryptionTypeOptions = [
  {
    value: eKeyTypes.eMaster,
    label: "'M' - Master Key",
  },
];

const macTypeOptions = [
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

const pinEncryptionPurposeOptions = [
  {
    value: eKeyPurpose.eMSPinEncryption,
    label: "'P' - Pin Encryption",
  },
];

const validDukptKeys = [
  eKeyType.eAesDukptBdk,
  eKeyType.eAesDukptInitial,
  eKeyType.eDukptBdkKey,
  eKeyType.eDukpt3DesBdkKey,
  eKeyType.eDukptInitialKey,
  eKeyType.eGenericBdk,
];

function isDukpt(keyType) {
  return validDukptKeys.includes(keyType);
}

function getKeyTypeOptions() {
  let keyOptions = [];
  if (isDukpt(props.keyType)) {
    keyOptions = dukptTypeOptions;
    state.displayKeyPurpose = false;
  } else if (props.keyType === eKeyType.eMasterSession) {
    keyOptions = masterTypeOptions;
    state.displayKeyPurpose = true;
  } else if (props.keyType === eKeyType.ePinEncryptionKey) {
    keyOptions = pinEncryptionTypeOptions;
    state.displayKeyPurpose = true;
  } else if (props.keyType === eKeyType.eMacKey) {
    keyOptions = macTypeOptions;
    state.displayKeyPurpose = true;
  }

  return keyOptions;
}

function getKeyPurposeOptions() {
  let keyPurposes = [];
  if (
    props.keyType === eKeyType.eMasterSession ||
    props.keyType === eKeyType.eMacKey
  ) {
    keyPurposes = keyPurposeOptions;
  } else if (props.keyType === eKeyType.ePinEncryptionKey) {
    keyPurposes = pinEncryptionPurposeOptions;
  }
  return keyPurposes;
}
</script>

<style scoped>
.dki-button {
  margin-top: 0.5rem;
}
</style>
