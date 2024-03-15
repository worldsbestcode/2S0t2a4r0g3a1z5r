<template>
  <Dropdown right>
    <template #button="{ on }">
      <button class="icon-button" v-on="on">
        <img src="/shared/static/icons/account.svg" />
      </button>
    </template>

    <header>Logged In Users:</header>
    <template v-for="user in users" :key="user">
      <div class="text-and-button-container">
        <span>
          {{ user }}
        </span>
        <ChangePasswordModal :user="user" />
      </div>
    </template>

    <header>Active Roles:</header>
    <p>
      {{ roles.join(", ") }}
    </p>

    <header>Active Profile:</header>
    <div v-for="user in users" :key="user" class="text-and-button-container">
      <span>
        {{ user }}
      </span>

      <ChcButton
        :disabled="user === activeProfile"
        small
        secondary
        @click="switchActiveProfile(user)"
      >
        {{ user === activeProfile ? "Active" : "Activate profile" }}
      </ChcButton>
    </div>

    <LogOutButton />
  </Dropdown>
</template>

<script setup>
import { computed } from "vue";
import { useStore } from "vuex";

import ChangePasswordModal from "$shared/components/ChangePasswordModal.vue";
import ChcButton from "$shared/components/ChcButton.vue";
import Dropdown from "$shared/components/Dropdown.vue";
import LogOutButton from "$shared/components/LogOutButton.vue";

const store = useStore();

const users = computed(() => store.state.auth.users.map((x) => x.name));
const roles = computed(() => store.state.auth.roles.map((x) => x.name));
const activeProfile = computed(() => store.state.profiles.activeProfile);

function switchActiveProfile(user) {
  store.commit("profiles/switchActiveProfile", user);
}
</script>

<style scoped>
.text-and-button-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.text-and-button-container + .text-and-button-container {
  margin-top: 0.75rem;
}
</style>
