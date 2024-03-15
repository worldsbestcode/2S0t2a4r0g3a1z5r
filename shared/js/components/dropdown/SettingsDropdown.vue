<template>
  <Dropdown right>
    <template #button="{ on }">
      <button class="icon-button" v-on="on">
        <img src="/shared/static/icons/settings-one.svg" />
      </button>
    </template>

    <header>CryptoHub Administration</header>
    <nav class="chc-links">
      <a class="chc-link" href="/admin/">Administration</a>
      <a v-if="showUserManagement" class="chc-link" href="/iam/">
        User Management
      </a>
      <a class="chc-link" href="/cuserv/">Service Management</a>
      <a
        v-if="showSystemManagement"
        class="chc-link"
        href="/cuserv/#/admin/Administration"
      >
        System Management
      </a>
    </nav>
  </Dropdown>
</template>

<script setup>
import { computed } from "vue";
import { useStore } from "vuex";

import Dropdown from "$shared/components/Dropdown.vue";

const store = useStore();

const showUserManagement = computed(
  () => store.state.auth.mgmtPerms.users || store.state.auth.mgmtPerms.roles
);
const showSystemManagement = computed(() => store.state.auth.mgmtPerms.legacy);
</script>

<style scoped>
.chc-links {
  display: grid;
}

.chc-links > .chc-link {
  font-size: 18px;
  padding: 0.25rem 0;
}
</style>
