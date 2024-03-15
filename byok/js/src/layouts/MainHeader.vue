<template>
  <header class="header">
    <div class="empty-space" />
    <router-link :to="{ name: 'landing' }">
      <img class="fx-logo" :src="logoFullUrl" />
    </router-link>
    <button class="ellipsis-button" @click="logout">
      <i class="fas fa-ellipsis-h" />
    </button>
  </header>
</template>

<script>
import logoFullUrl from "/fx_logo_full_official.png";

export default {
  name: "MainHeader",
  setup: function () {
    return { logoFullUrl };
  },
  methods: {
    logout: function () {
      this.$httpV2
        .post("/logout", {}, { errorContextMessage: "Failed to log out" })
        .finally(() => {
          location.assign("/");
        });
    },
  },
};
</script>

<style scoped>
.header {
  height: var(--main-header-height);
  position: fixed;
  left: 0;
  right: 0;
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(238, 238, 238, 1) 100%
  );
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-space {
  width: var(--main-sidebar-width);
}

.fx-logo {
  height: 24px;
}

.ellipsis-button {
  height: var(--main-header-height);
  width: var(--main-header-height);
  border-radius: 0px;
  border: none;
  border-left: 1px solid var(--border-color);
  color: inherit;
  font-size: 13px;
  background: transparent;
  padding: 0;
}

.ellipsis-button:hover {
  background-color: #e6e6e6;
}

.ellipsis-button:active {
  background: #d4d4d4;
  box-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125);
}
</style>
