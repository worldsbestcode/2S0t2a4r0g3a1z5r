<template>
  <ChcInput
    v-model="store.state.idp.adminUser"
    label="Admin login"
    hint="Used to search for matching users and roles"
    placeholder="cn=Admin,ou=Users,dc=example,dc=com"
  />
  <ChcInput
    v-model="store.state.idp.adminPassword"
    label="Password"
    type="password"
  />
</template>

<script setup>
import { useStore } from "vuex";

import ChcInput from "$shared/components/ChcInput.vue";

const store = useStore();
</script>
