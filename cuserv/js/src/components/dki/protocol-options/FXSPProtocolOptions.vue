<template>
  <DKIKeyInput
    v-model:fx-key="key"
    class="key-input"
    :key-restriction-set="keyRestrictionSet"
    title="KBPK"
    @keyUpdated="updateOptions"
  />
</template>

<script setup>
import axios from "axios";
import { defineEmits, defineProps, onBeforeMount, ref } from "vue";

import {
  eKeyLength,
  eKeyType,
  FXKey,
  KeyRestrictionSet,
} from "$shared/utils/keys.js";

import DKIKeyInput from "@/components/dki/DKIKeyInput.vue";

const emit = defineEmits(["update:options"]);
const props = defineProps({
  options: {
    type: Object,
    required: true,
  },
});
const key = ref(new FXKey());
const keyRestrictionSet = ref(new KeyRestrictionSet());

function updateOptions() {
  let options = props.options;
  options.kbpk = key.value.uuid;
  emit("update:options", options);
}

onBeforeMount(() => {
  axios.get(`/dki/v1/keys/${props.options.kbpk}`).then((response) => {
    let zmk = response.data;
    key.value.uuid = zmk.uuid;
    key.value.name = zmk.name;
  });
  keyRestrictionSet.value.setComboArray(eKeyType.eKeyTransferKey, [
    eKeyLength.eAES256,
    eKeyLength.eAES192,
    eKeyLength.eAES128,
    eKeyLength.e2DES3,
    eKeyLength.e3DES3,
  ]);
});
</script>

<style scoped>
.key-input {
  max-width: 800px;
}
</style>
