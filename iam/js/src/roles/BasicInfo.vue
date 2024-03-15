<template>
  <ChcInput
    v-model="store.state.role.name"
    hint="length 4-128"
    label="Role Name"
    placeholder="Name"
    :readonly="store.state.role.uuid !== null"
  />
  <ChcComboBox
    v-model="store.state.role.requiredLogins"
    hint=""
    label="Login Count Requirement"
    :values="dualControlValues"
  />
  <ChcCheckBox
    v-if="store.state.role.uuid === null"
    v-model="store.state.role.hardened"
    hint="Hardened"
    :label="store.state.role.management ? 'HSM Role' : 'HSM Partition'"
  />
  <ChcComboBox
    v-model="store.state.role.principal"
    hint="Auxiliary roles do not inherit key and object permissions"
    label="Role Type"
    :values="principalValues"
    :disabled="store.state.role.uuid !== null"
  />
  <ChcCheckBox
    v-if="store.state.role.uuid !== null"
    v-model="store.state.role.archive"
    hint="Hidden and not active"
    label="Archived"
  />
</template>

<script setup>
import { computed, defineEmits, defineProps, ref } from "vue";
import { useStore } from "vuex";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcInput from "$shared/components/ChcInput.vue";

import ChcCheckBox from "@/components/ChcCheckBox.vue";

const dualControlValues = ref([
  { value: "1", label: "Normal" },
  { value: "2", label: "2 Logins Required" },
  { value: "3", label: "3 Logins Required" },
]);

const principalValues = ref([
  { value: "1", label: "Principal" },
  { value: "0", label: "Auxiliary" },
]);

const store = useStore();
</script>
