<template>
  <label class="chc-label">
    <span class="chc-label__text">
      {{ title }}
      <span v-if="hint" class="chc-label__hint">
        {{ hint }}
      </span>
    </span>
    <div class="key-container">
      <div v-if="fxKey.uuid">{{ fxKey.name }}</div>
      <div v-else class="key-name-muted">No key selected</div>
      <Modal title="Select Key">
        <template #button="{ on }">
          <ButtonIcon
            v-if="fxKey.uuid"
            class="key-action"
            icon="pencil"
            v-on.stop="on"
          />
          <button v-else class="icon-with-hover key-action" v-on.stop="on">
            <img src="/shared/static/add-circle-inactive.svg" />
            <img src="/shared/static/add-circle.svg" />
          </button>
        </template>
        <template #content="{ toggleModal }">
          <DKIKeySelector
            :key-restriction-set="keyRestrictionSet"
            @cancel="toggleModal"
            @keySelected="(key) => handleKeySelected(key, toggleModal)"
          />
        </template>
      </Modal>
    </div>
  </label>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import Modal from "$shared/components/Modal.vue";
import { KeyRestrictionSet } from "$shared/utils/keys.js";

import ButtonIcon from "@/components/ButtonIcon.vue";
import DKIKeySelector from "@/components/dki/DKIKeySelector.vue";

const emit = defineEmits(["update:fxKey", "keyUpdated"]);
const props = defineProps({
  fxKey: {
    type: Object,
    required: true,
  },
  hint: {
    type: String,
    default: undefined,
  },
  title: {
    type: String,
    required: true,
  },
  keyRestrictionSet: {
    type: KeyRestrictionSet,
    default: new KeyRestrictionSet(),
    required: false,
  },
});

const fxKey = computed({
  get() {
    return props.fxKey;
  },
  set(value) {
    emit("update:fxKey", value);
  },
});

function addKey(key) {
  fxKey.value = key;
  emit("keyUpdated");
}

function handleKeySelected(key, toggleModal) {
  addKey(key);
  toggleModal();
}
</script>

<style scoped>
.key-container {
  display: flex;
  cursor: pointer;
  padding: 0rem 0.4rem;
  border: 1px solid var(--border-color);
  border-radius: 3px;
  height: 50px;
  justify-content: space-between;
  align-items: center;
}

.key-action {
  border-left: 1px solid var(--border-color);
  padding-left: 0.4rem;
}

.key-name-muted {
  color: var(--muted-text-color);
}
</style>
