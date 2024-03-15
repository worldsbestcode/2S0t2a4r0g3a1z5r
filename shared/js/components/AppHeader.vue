<template>
  <template v-if="loggedIn">
    <header
      v-bind="$attrs"
      class="shared-app-header chc-main-horizontal-padding"
    >
      <nav class="shared-app-header-nav">
        <a href="/cuserv/" class="shared-app-header-nav__img-wrapper">
          <img
            class="shared-app-header-nav__img"
            src="/shared/static/crypto-hub-futurex-color.png"
          />
        </a>

        <a
          v-if="location.pathname !== '/cuserv/'"
          href="/cuserv/"
          class="chc-main-link"
        >
          Service Manager
        </a>
      </nav>

      <div class="shared-button-dropdowns">
        <NotificationsDropdown
          v-if="permissions.includes('System:Administration')"
        />

        <SupportDropdown />
        <SystemDropdown v-if="permissions.includes('Device:Config')" />
        <SettingsDropdown v-if="permissions.includes('Device:Reboot')" />
        <AccountDropdown />
      </div>
    </header>
  </template>

  <LoadingRouter />
</template>

<script setup>
import AccountDropdown from "$shared/components/dropdown/AccountDropdown.vue";
import NotificationsDropdown from "$shared/components/dropdown/NotificationsDropdown.vue";
import SettingsDropdown from "$shared/components/dropdown/SettingsDropdown.vue";
import SupportDropdown from "$shared/components/dropdown/SupportDropdown.vue";
import SystemDropdown from "$shared/components/dropdown/SystemDropdown.vue";
import LoadingRouter from "$shared/components/LoadingRouter.vue";
import { useLoggedIn, usePermissions } from "$shared/composables.js";

const loggedIn = useLoggedIn();
const permissions = usePermissions();

const location = window.location;
</script>

<style scoped>
.shared-app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  height: var(--app-header-height);

  font-family: "Roboto";

  background-color: var(--primary-background-color);
  color: var(--primary-text-color);
}

.shared-app-header-nav {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.shared-app-header-nav__img-wrapper {
  height: calc(var(--app-header-height) - 16px);
  display: block;
}

.shared-app-header-nav__img {
  height: 100%;
}

.shared-button-dropdowns {
  display: flex;
  gap: 1rem;
  height: 100%;
  align-items: center;
}
</style>
