<template>
  <ChcInput
    v-model="store.state.user.username"
    hint="length 4-128"
    :label="store.state.user.application ? 'Login Name' : 'Username'"
    :placeholder="store.state.user.application ? 'Name' : 'Username'"
    :readonly="store.state.user.uuid !== null"
  />
  <ChcInput
    v-model="store.state.user.commonName"
    hint="length 0-128"
    label="Common Name"
    placeholder="Common Name"
  />
  <ChcInput
    v-if="!store.state.user.application"
    v-model="store.state.user.givenName"
    hint="length 0-128"
    label="Given Name"
    placeholder="Given Name"
  />
  <ChcInput
    v-if="!store.state.user.application"
    v-model="store.state.user.surname"
    hint="length 0-128"
    label="Surname"
    placeholder="Surname"
  />
  <ChcInput
    v-if="!store.state.user.application"
    v-model="store.state.user.email"
    hint="length 0-128"
    label="Email"
    placeholder="Email"
  />
  <ChcInput
    v-if="!store.state.user.application"
    v-model="store.state.user.mobilePhone"
    hint="Decimal"
    label="Mobile Phone Number"
    placeholder="Mobile"
  />
  <ChcComboBox
    v-if="!store.state.user.application"
    v-model="store.state.user.mobileCarrier"
    hint="For SMS Notifications"
    label="Phone Carrier"
    :values="values"
  />
  <ChcCheckBox
    v-if="store.state.user.uuid === null"
    v-model="store.state.user.hardened"
    :hint="store.state.user.application ? 'HSM Application' : 'HSM User'"
    :label="store.state.user.application ? 'HSM Application' : 'HSM User'"
  />
  <ChcCheckBox
    v-model="store.state.user.locked"
    hint="Login disabled"
    label="Locked"
  />
  <ChcCheckBox
    v-if="store.state.user.uuid !== null"
    v-model="store.state.user.archive"
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

const values = ref([
  { value: "None", label: "" },
  { value: "ATT", label: "AT&T" },
  { value: "Alltell", label: "Alltell" },
  { value: "Boost", label: "Boost" },
  { value: "Comcast", label: "Comcast" },
  { value: "MTNGroup", label: "MTN Group" },
  { value: "Qwest", label: "Qwest" },
  { value: "Rogers", label: "Rogers" },
  { value: "Sprint", label: "Sprint" },
  { value: "Tmobile", label: "T-Mobile" },
  { value: "Trac", label: "Trac" },
  { value: "Verizon", label: "Verizon" },
  { value: "Virgin", label: "Virgin" },
  { value: "Vodacom", label: "Vodacom" },
]);

const store = useStore();
</script>
