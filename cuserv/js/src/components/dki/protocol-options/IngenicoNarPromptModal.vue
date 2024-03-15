<template>
  <Modal title="Add Prompt">
    <template #button="{ on }">
      <ChcButton
        class="dki-button"
        secondary
        small
        img="/shared/static/element-plus.svg"
        v-on="on"
      >
        Add Prompt
      </ChcButton>
    </template>
    <template #content="{ toggleModal }">
      <ChcComboBox
        v-model:modelValue="prompt.key"
        label="Key"
        :values="keyValues"
      />
      <ChcSpinner
        v-model:modelValue="prompt.app"
        title="App"
        min="0"
        step="1"
        max="300"
      />
      <ChcSpinner
        v-model:modelValue="prompt.index"
        title="Index"
        min="0"
        step="1"
        max="300"
      />

      <ChcInput v-model:modelValue="prompt.prompt" label="Prompt" />

      <ModalFooter
        text="Add"
        @cancel="toggleModal"
        @action="
          () => {
            toggleModal();
            addPrompt();
          }
        "
      />
    </template>
  </Modal>
</template>

<script setup>
import { defineEmits } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcSpinner from "$shared/components/ChcSpinner.vue";
import Modal from "$shared/components/Modal.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

const emit = defineEmits(["addPrompt"]);

function resetPrompt() {
  return {
    key: "PEFMK",
    app: 0,
    index: 0,
    prompt: "",
  };
}

let prompt = resetPrompt();

const keyValues = [
  {
    label: "PEFMK",
    value: "PEFMK",
  },
  {
    label: "CEFMK",
    value: "CEFMK",
  },
];

function addPrompt() {
  emit("addPrompt", { ...prompt });
  prompt = resetPrompt();
}
</script>

<style scoped>
.dki-button {
  margin-top: 0.8rem;
}
</style>
