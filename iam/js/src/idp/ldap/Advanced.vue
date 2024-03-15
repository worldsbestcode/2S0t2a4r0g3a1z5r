<template>
  <ChcInput
    v-model="store.state.idp.memberField"
    label="Group membership attribute (On group)"
    placeholder="member"
  />

  <ChcInput
    v-model="store.state.idp.memberOfField"
    label="Group membership attribute (On user)"
    placeholder="memberOf"
  />

  <ChcComboBox
    v-model="store.state.idp.loginMode"
    label="Login method"
    :values="loginModes"
  />
</template>

<script setup>
import { useStore } from "vuex";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcInput from "$shared/components/ChcInput.vue";

const loginModes = [
  { value: "Simple", label: "Simple" },
  { value: "DIGEST-MD5", label: "DIGEST-MD5" },
];

const store = useStore();
</script>
