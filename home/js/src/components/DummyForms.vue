<template>
  <form v-for="(user, index) in usersNonExpired" :key="user.id">
    <p>Identity {{ index + 1 }} login</p>
    <input class="chc-input" disabled :placeholder="user.name" />
  </form>
</template>

<script setup>
import { computed } from "vue";
import { useStore } from "vuex";

const store = useStore();

const usersNonExpired = computed(() =>
  store.state.auth.users.filter(
    (user) => !user.expired || (user.expired && user.defaultPw),
  ),
);
</script>
