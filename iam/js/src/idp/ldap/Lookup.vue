<template>
  <ChcCheckBox
    v-model="store.state.idp.requireLocal"
    label="Require local identity"
    hint="Prevent usernames not registered on CryptoHub"
  />

  <UserIdTypeComboBox />

  <ChcInput
    v-model="store.state.idp.userField"
    label="LDAP attribute to match against login username"
    placeholder="cn"
  />

  <ChcInput
    v-model="store.state.idp.userBaseDn"
    label="User base DN"
    hint="Location to search for users"
    placeholder="ou=Users,dc=example,dc=com"
  />

  <RoleIdTypeComboBox v-if="!store.state.idp.requireLocal" />

  <ChcInput
    v-if="!store.state.idp.requireLocal"
    v-model="store.state.idp.roleField"
    label="LDAP attribute to match against role"
    placeholder="cn"
  />

  <ChcInput
    v-if="!store.state.idp.requireLocal"
    v-model="store.state.idp.roleBaseDn"
    label="Role base DN"
    hint="Location to search for groups/roles"
    placeholder="ou=Groups,dc=example,dc=com"
  />
</template>

<script setup>
import { useStore } from "vuex";

import ChcInput from "$shared/components/ChcInput.vue";

import ChcCheckBox from "@/components/ChcCheckBox.vue";
import RoleIdTypeComboBox from "@/idp/RoleIdTypeComboBox.vue";
import UserIdTypeComboBox from "@/idp/UserIdTypeComboBox.vue";

const store = useStore();
</script>
