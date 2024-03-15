<template>
  <ChcToggle
    v-model:modelValue="terminalBased"
    small
    side="right"
    label="Set Terminal-Based keys"
  ></ChcToggle>
  <ChcToggle
    v-model:modelValue="keyPattern"
    small
    class="dki-toggle"
    side="right"
    label="Set Key Pattern 4"
  ></ChcToggle>
  <ChcToggle
    v-model:modelValue="macPrompts"
    small
    side="right"
    label="MAC Prompts"
  ></ChcToggle>
  <ChcToggle
    v-model:modelValue="serialNumberFirst"
    small
    side="right"
    label="Inject Serial Number Before All Other Keys"
  ></ChcToggle>
  <ChcToggle
    v-model:modelValue="eraseAfterSn"
    small
    side="right"
    label="Erase Key After Serial Number Injection"
  ></ChcToggle>
  <ChcComboBox
    v-model:modelValue="macLength"
    class="dki-combobox"
    label="MAC Calculation"
    :values="values"
  ></ChcComboBox>

  <table class="deployed-manage-table">
    <thead>
      <tr>
        <th>Key</th>
        <th>App</th>
        <th>Index</th>
        <th>Prompt</th>
        <th>action</th>
      </tr>
    </thead>
    <tbody>
      <tr v-if="promptMessages.length === 0">
        <td :colspan="5" style="text-align: center">No Prompts</td>
      </tr>
      <tr v-for="(prompt, index) in promptMessages" v-else :key="index">
        <td>{{ prompt.key }}</td>
        <td>{{ prompt.app }}</td>
        <td>{{ prompt.index }}</td>
        <td>{{ prompt.prompt }}</td>
        <td>
          <button
            class="deployed-manage-table__delete"
            @click="promptMessages.splice(index, 1)"
          >
            delete
          </button>
        </td>
      </tr>
    </tbody>
  </table>

  <IngenicoNarPromptModal @addPrompt="addPrompt"></IngenicoNarPromptModal>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";

import IngenicoNarPromptModal from "@/components/dki/protocol-options/IngenicoNarPromptModal.vue";

const emit = defineEmits(["update:options"]);
const props = defineProps({
  options: {
    type: Object,
    required: true,
  },
});

const terminalBased = computed({
  get() {
    return props.options.terminalBased;
  },
  set(value) {
    let options = props.options;
    options.terminalBased = value;
    emit("update:options", options);
  },
});

const keyPattern = computed({
  get() {
    return props.options.keyPattern;
  },
  set(value) {
    let options = props.options;
    options.keyPattern = value;
    emit("update:options", options);
  },
});

const macPrompts = computed({
  get() {
    return props.options.macPrompts;
  },
  set(value) {
    let options = props.options;
    options.macPrompts = value;
    emit("update:options", options);
  },
});

const serialNumberFirst = computed({
  get() {
    return props.options.injectSerialNumberFirst;
  },
  set(value) {
    let options = props.options;
    options.injectSerialNumberFirst = value;
    emit("update:options", options);
  },
});

const eraseAfterSn = computed({
  get() {
    return props.options.eraseAfterSn;
  },
  set(value) {
    let options = props.options;
    options.eraseAfterSn = value;
    emit("update:options", options);
  },
});

const macLength = computed({
  get() {
    return props.options.macLength;
  },
  set(value) {
    let options = props.options;
    options.macLength = value;
    emit("update:options", options);
  },
});

const promptMessages = computed({
  get() {
    return props.options.promptMessages;
  },
  set(value) {
    let options = props.options;
    options.promptMessages = value;
    emit("update:options", options);
  },
});

const values = [
  {
    label: "Don't Change",
    value: "DontChange",
  },
  {
    label: "Double Length",
    value: "DoubleLength",
  },
  {
    label: "Single Length",
    value: "SingleLength",
  },
];

function addPrompt(prompt) {
  promptMessages.value.push(prompt);
}
</script>

<style scoped>
.dki-combobox {
  width: 40px;
}
</style>
