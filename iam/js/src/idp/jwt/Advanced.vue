<template>
  <ChcInput
    v-model="store.state.idp.leeway"
    label="Leeway"
    hint="Max seconds mismatch with provider's time"
    placeholder="Seconds"
    :inputSanitize="numbersOnly"
  />
  <ChcCheckBox
    v-model="store.state.idp.enforceDualFactor"
    label="Enforce dual-factor"
    hint="Prevent identities that have dual-factor login requirements"
  />
</template>

<script setup>
import { useStore } from "vuex";

import ChcInput from "$shared/components/ChcInput.vue";

import ChcCheckBox from "@/components/ChcCheckBox.vue";

// XXX: Need a spinbox widget
function numbersOnly(value) {
  return value.replace(/\D/g, "");
}

const store = useStore();
</script>
