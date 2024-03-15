<template>
  <ChcComboBox
    v-model="store.state.idp.userIdType"
    label="User Match Type"
    hint="How to match the user field to an identity"
    v-bind="$props"
    :values="userIdTypes"
  />
</template>

<script setup>
import { ref } from "vue";
import { useStore } from "vuex";

import ChcComboBox from "$shared/components/ChcComboBox.vue";

const userIdTypes = ref([
  { value: "Username", label: "Username" },
  { value: "Email", label: "Email" },
  { value: "UUID", label: "UUID" },
]);

const store = useStore();
</script>
