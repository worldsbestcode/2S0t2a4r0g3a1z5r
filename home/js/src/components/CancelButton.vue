<template>
  <form v-if="users.length > 0 && !loggedIn" @submit.prevent="logout">
    <button class="button-secondary" :disabled="props.loading">Cancel</button>
  </form>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";
import { useStore } from "vuex";

import { useLoggedIn } from "$shared/composables.js";

const emit = defineEmits(["cancelled"]);

const store = useStore();
const loggedIn = useLoggedIn();

const props = defineProps({
  loading: {
    type: Boolean,
  },
});

const users = computed(() => store.state.auth.users);

async function logout() {
  store.dispatch("auth/logout").finally(() => {
    emit("cancelled");
  });
}
</script>
