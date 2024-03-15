<template>
  <ChcCheckBox
    v-model="store.state.idp.requireLocal"
    label="Require local identity"
    hint="Prevent usernames not registered on CryptoHub"
  />

  <ChcInput
    v-model="store.state.idp.userField"
    label="User field"
    hint="The field in the JWT that matches to an identity"
    placeholder="sub"
  />

  <UserIdTypeComboBox />

  <ChcComboBox
    v-if="!store.state.idp.requireLocal"
    v-model="store.state.idp.rolesFromToken"
    label="Role match type"
    hint="For identities not registered on CryptoHub"
    :values="roleMatchTypes"
  />

  <ChcInput
    v-if="
      !store.state.idp.requireLocal &&
      store.state.idp.rolesFromToken === 'Token'
    "
    v-model="store.state.idp.roleField"
    label="Roles field"
    hint="The field in the JWT that defines authorized roles"
    placeholder="roles"
  />

  <RoleIdTypeComboBox
    v-if="
      !store.state.idp.requireLocal &&
      store.state.idp.rolesFromToken === 'Token'
    "
  />

  <div
    v-if="
      !store.state.idp.requireLocal &&
      store.state.idp.rolesFromToken !== 'Token'
    "
  >
    TODO: Fuzzy search to assign predefined roles
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useStore } from "vuex";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcInput from "$shared/components/ChcInput.vue";

import ChcCheckBox from "@/components/ChcCheckBox.vue";
import RoleIdTypeComboBox from "@/idp/RoleIdTypeComboBox.vue";
import UserIdTypeComboBox from "@/idp/UserIdTypeComboBox.vue";

const roleMatchTypes = ref([
  { value: "Token", label: "From token" },
  { value: "Database", label: "Predefined" },
]);

const store = useStore();
</script>
