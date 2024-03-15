<template>
  <ChcComboBox
    v-model="store.state.idp.roleIdType"
    label="Role Match Type"
    hint="How to match the role field to a role"
    v-bind="$props"
    :values="roleIdTypes"
  />
</template>

<script setup>
import { ref } from "vue";
import { useStore } from "vuex";

import ChcComboBox from "$shared/components/ChcComboBox.vue";

const roleIdTypes = ref([
  { value: "Name", label: "Name" },
  { value: "External Name", label: "External Name" },
  { value: "UUID", label: "UUID" },
]);

const store = useStore();
</script>
