<template>
  <div v-for="(claim, index) in store.state.idp.claims" class="container">
    <ChcInput
      v-model="store.state.idp.claims[index].claim"
      label="Claim"
      hint="field"
    />
    <ChcCheckBox
      v-model="store.state.idp.claims[index].plural"
      label="Allow plural"
      hint="Allow plural version of claim string"
    />
    <ChcCheckBox
      v-model="store.state.idp.claims[index].requireAll"
      label="Require all"
      hint="Require all values or a single match"
    />
    <br />
    <B>Values</B>
    <div v-for="(value, valueindex) in claim.values" class="container">
      <input v-model="store.state.idp.claims[index].values[valueindex]" />
      <button
        value="-"
        @click="store.state.idp.claims[index].values.splice(valueindex, 1)"
      >
        -
      </button>
    </div>
    <button @click="store.state.idp.claims[index].values.push('')">+</button>
    <br />
    <br />
    <ChcButton
      img="/shared/static/trash-active.svg"
      @click="store.state.idp.claims.splice(index, 1)"
    >
      REMOVE CLAIM
    </ChcButton>
  </div>
  <br />
  <ChcButton img="/shared/static/element-plus.svg" @click="addClaim()">
    ADD CLAIM
  </ChcButton>
  <br />
  <br />
</template>

<script setup>
import { useStore } from "vuex";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";

import ChcCheckBox from "@/components/ChcCheckBox.vue";

const store = useStore();

function addClaim() {
  store.state.idp.claims.push({
    claim: "",
    plural: false,
    requireAll: true,
    values: [""],
  });
}
</script>

<style scoped>
.container {
  border: 1px solid black;
  padding: 10px;
}
</style>
