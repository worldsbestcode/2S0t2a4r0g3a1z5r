<template>
  <main class="app-main chc-main-horizontal-padding">
    <h1 class="service-management-text">Identity &amp; Access Management</h1>

    <div class="service-management-actions-container">
      <div class="service-management-actions">
        <RouterLink
          v-for="link in views"
          active-class="service-management-button-link-active"
          class="service-management-button-link"
          :to="link.to"
        >
          {{ link.text }}
        </RouterLink>
      </div>
    </div>

    <div class="service-manager-actions-seperator" />

    <RouterView />
  </main>
</template>

<script setup>
import { reactive, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";

const route = useRoute();
const router = useRouter();
const store = useStore();

let views = [];

if (store.state.auth.mgmtPerms.users) {
  views.push({
    to: { name: "users" },
    text: "Users",
  });
  views.push({
    to: { name: "apps" },
    text: "Applications",
  });
}

if (store.state.auth.mgmtPerms.roles) {
  views.push({
    to: { name: "roles" },
    text: "Roles",
  });
  views.push({
    to: { name: "partitions" },
    text: "Partitions",
  });
}

if (store.state.auth.mgmtPerms.admin) {
  views.push({
    to: { name: "idp" },
    text: "Identity Providers",
  });
}

watchEffect(() => {
  if (route.name === "landing") {
    router.replace({ name: "users" });
  }
});
</script>

<style>
.service-management-text {
  font-weight: 900;
  font-size: 48px;
  margin-bottom: 1.25rem;
}

.service-management-button-link {
  color: var(--primary-text-color);
  font-weight: 500;
  border: 0;
  background: none;
  padding: 0;
  text-decoration: none;
  align-self: center;
}

.service-management-button-link:hover,
.service-management-button-link-active {
  color: var(--primary-color);
  text-decoration: underline;
}

.service-management-actions-container {
  display: flex;
  justify-content: space-between;
  padding-bottom: 1.5rem;
}

.service-management-actions {
  display: flex;
  gap: 2rem;
}

.service-manager-actions-seperator {
  height: 1px;
  background: var(--border-color);
}
</style>
