<template>
  <WizardPage
    title="Select exisiting keys"
    description="This service uses keys that exist on the system.
                 These keys must be defined/selected before service can be deployed."
  >
    <div class="keys-list">
      <div v-for="(key, index) in state.keys" :key="key.name">
        <DKIKeyInput
          v-model:fx-key="state.keys[index]"
          :title="state.templateKeys[index].name"
          :key-restriction-set="getKeyRestiction(key)"
          @keyUpdated="handleKeyUpdated(index)"
        />
      </div>
    </div>
  </WizardPage>
</template>

<script setup>
import axios from "axios";
import {
  computed,
  defineEmits,
  defineProps,
  onBeforeMount,
  reactive,
} from "vue";

import WizardPage from "$shared/components/wizard/WizardPage.vue";
import { FXKey, KeyRestrictionSet } from "$shared/utils/keys.js";

import DKIKeyInput from "@/components/dki/DKIKeyInput.vue";

const emit = defineEmits(["update:existingKeys"]);

const props = defineProps({
  templateUuid: {
    type: String,
    required: true,
  },
  existingKeys: {
    type: Array,
    required: true,
  },
});

const state = reactive({
  keys: [],
  templateKeys: [],
});

const existingKeys = computed({
  get() {
    return props.existingKeys;
  },
  set(value) {
    emit("update:existingKeys", value);
  },
});

onBeforeMount(() => {
  axios
    .get(`/cuserv/v1/templates/${props.templateUuid}`, {
      errorContext: "Failed to fetch template details",
    })
    .then((response) => {
      if (response.status === 200) {
        response.data.params.keys.forEach((key) => {
          if (key.origin === "Existing") {
            let fxKey = new FXKey();
            fxKey.fromProtoKey(key);
            state.keys.push(fxKey);
            state.templateKeys.push(fxKey);
          }
        });
      }
    });
});

function handleKeyUpdated(index) {
  let templateKey = state.templateKeys[index];
  state.keys[index].tag = templateKey.name;
  existingKeys.value = state.keys;
}

function getKeyRestiction(key) {
  let keyRestictionSet = new KeyRestrictionSet();
  keyRestictionSet.setCombo(key.eKeyType, key.eKeyLength);
  return keyRestictionSet;
}
</script>

<style scoped>
.keys-list {
  display: block;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}
</style>
