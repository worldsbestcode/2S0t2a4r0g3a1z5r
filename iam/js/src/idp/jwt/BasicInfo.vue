<template>
  <ChcInput
    v-model="store.state.idp.name"
    label="Name"
    hint="length 3-128"
    placeholder="Name"
  />
  <ChcInput
    v-model="store.state.idp.issuer"
    label="Issuer"
    hint="iss field in token"
    placeholder="Token Issuer"
  />
</template>

<script setup>
import { useStore } from "vuex";

import ChcInput from "$shared/components/ChcInput.vue";

const store = useStore();
</script>
