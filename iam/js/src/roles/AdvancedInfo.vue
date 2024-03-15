<template>
  <ChcInput
    v-model="store.state.role.externalName"
    hint="Name used by identity providers (Ex: LDAP)"
    label="External Name"
    :placeholder="Name"
  />
  <ChcComboBox
    v-if="store.state.role.users"
    v-model="store.state.role.dualFactorRequired"
    label="Dual-factor requirement"
    hint="Note: 'Always Required' prevents login if no credential is enrolled"
    :values="dualFactorValues"
  />
  <ChcCheckBox
    v-if="store.state.role.users"
    v-model="store.state.role.webLogin"
    hint="Able to login through web page"
    label="Web Login"
  />
  <ChcCheckBox
    v-if="store.state.role.users"
    v-model="store.state.role.localLogin"
    hint="Able to login to hardware device desktop"
    label="Hardware Login"
  />
  <ChcCheckBox
    v-if="store.state.role.users"
    v-model="store.state.role.apiLogin"
    hint="Able to login through programmable APIs"
    label="API Login"
  />
  <ChcCheckBox
    v-if="!store.state.role.users"
    v-model="store.state.role.restLogin"
    hint="Able to login through REST API"
    label="REST API Login"
  />
  <ChcCheckBox
    v-if="!store.state.role.users"
    v-model="store.state.role.excryptLogin"
    hint="Able to login through Excrypt API"
    label="Excrypt API Login"
  />
  <ChcCheckBox
    v-if="!store.state.role.users"
    v-model="store.state.role.kmipLogin"
    hint="Able to login through KMIP API"
    label="KMIP API Login"
  />
  <ChcCheckBox
    v-if="
      store.state.role.users &&
      store.state.role.hardened &&
      store.state.role.requiredLogins >= 2
    "
    v-model="store.state.role.upgradePerms"
    hint="Inherit new permissions and control system roles"
    label="Administrator"
  />
</template>

<script setup>
import { ref } from "vue";
import { useStore } from "vuex";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcInput from "$shared/components/ChcInput.vue";

import ChcCheckBox from "@/components/ChcCheckBox.vue";

const dualFactorValues = ref([
  { value: "Never", label: "Never" },
  { value: "Available", label: "If User Has Credential Enrolled" },
  { value: "Always", label: "Always Required" },
]);

const store = useStore();
</script>
