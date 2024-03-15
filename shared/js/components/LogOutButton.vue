<template>
  <ChcButton
    style="width: 100%; margin-top: 1rem"
    :loading="state.loading"
    @click="logOut"
  >
    Log out
  </ChcButton>
</template>

<script setup>
import { reactive } from "vue";
import { useStore } from "vuex";

import { sendToLogin } from "$shared";
import ChcButton from "$shared/components/ChcButton.vue";

const store = useStore();

const state = reactive({
  loading: false,
});

function logOut() {
  state.loading = true;
  store.dispatch("auth/logout").finally(() => {
    sendToLogin();
    state.loading = false;
  });
}
</script>
