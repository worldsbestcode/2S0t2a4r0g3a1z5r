<template>
  <WizardFuzzyInput
    v-model:selected="state.selectedKey"
    single
    :data="state.keyNames"
    :display="getDisplayName"
    :keys="['name']"
    no-search-results="No keys found"
    placeholder="Search for key name"
  />
  <div class="modal-button-bottom">
    <button class="button-secondary" @click="emit('cancel')">CANCEL</button>
    <button
      class="button-primary"
      :disabled="!state.isKeySelected"
      @click="addKey"
    >
      ADD KEY
    </button>
  </div>
</template>

<script setup>
import axios from "axios";
import { defineEmits, defineProps, onBeforeMount, reactive, watch } from "vue";

import {
  eKeyLengthToString,
  eKeyTypeToString,
  FXKey,
  KeyRestrictionSet,
} from "$shared/utils/keys.js";

import WizardFuzzyInput from "@/components/wizard/WizardFuzzyInput.vue";

const emit = defineEmits(["cancel", "keySelected"]);

const props = defineProps({
  keyRestrictionSet: {
    type: KeyRestrictionSet,
    default: new KeyRestrictionSet(),
    required: false,
  },
});

const state = reactive({
  selectedKey: "",
  keys: [],
  keyNames: [],
  page: 1,
  pageSize: 15,
  totalPages: 1,
  isKeySelected: false,
});

function addKey() {
  let key = getKey();
  if (key) {
    emit("keySelected", key);
  }
}

onBeforeMount(() => {
  axios
    .post(
      "/dki/v1/keys/query",
      {
        restrictedKeys: props.keyRestrictionSet.flatten(),
      },
      {
        errorContext: "Failed to query keys",
      },
    )
    .then((response) => {
      state.keys = [];
      if (response.data.keys) {
        response.data.keys.forEach((key) => {
          let fxKey = new FXKey(key.uuid, key.name, key.type, key.length);
          state.keys.push(fxKey);
          state.keyNames.push(fxKey.name);
        });
      }
    });
});

function getDisplayName(keyName) {
  let displayName = keyName;

  state.keys.forEach((key) => {
    if (key.name == keyName) {
      displayName += " - " + eKeyTypeToString(key.eKeyType);
      displayName += " - " + eKeyLengthToString(key.eKeyLength);
    }
  });

  return displayName;
}

function getKey() {
  return state.keys.find((key) => key.name.trim() === state.selectedKey.trim());
}

watch(state, () => {
  let key = getKey();
  state.isKeySelected = key !== undefined;
});
</script>

<style scoped>
.key-table {
  margin-top: 0rem;
}
.key-table tr th + th,
.key-table tr td + td {
  padding: 0rem 2rem;
}
.modal-button-bottom {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  justify-content: space-between;
}

.selected {
  background: var(--border-color);
  color: var(--primary-color);
}

.selected td:first-child {
  color: var(--primary-color);
}
</style>
