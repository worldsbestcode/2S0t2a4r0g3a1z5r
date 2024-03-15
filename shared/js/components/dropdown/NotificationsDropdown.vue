<template>
  <Dropdown right>
    <template #button="{ on }">
      <button class="icon-button" v-on="on">
        <img src="/shared/static/icons/notification.svg" />
        <div v-if="hasNotifications" class="notifications-badge" />
      </button>
    </template>

    <header class="notifications-header">Notifications</header>
    <div v-if="hasNotifications" class="notifications-container">
      <template
        v-for="notification in notifications"
        :key="notification.objInfo.uuid"
      >
        <a
          v-if="adminLink(notification.setupStepType)"
          :href="adminLink(notification.setupStepType)"
          class="notification"
        >
          <NotificationsDropdownNotification :notification="notification" />
        </a>
        <Modal v-else :title="notification.objInfo.name">
          <template #button="{ on }">
            <button class="notification" v-on="on">
              <NotificationsDropdownNotification :notification="notification" />
            </button>
          </template>
          <template #content>
            {{ notification.messageText }}
          </template>
        </Modal>
      </template>
    </div>
    <div v-else>There are no notifications.</div>
  </Dropdown>
</template>

<script setup>
import { computed } from "vue";
import { useStore } from "vuex";

import { adminLink } from "$shared/admin.js";
import Dropdown from "$shared/components/Dropdown.vue";
import Modal from "$shared/components/Modal.vue";
import NotificationsDropdownNotification from "$shared/components/NotificationsDropdownNotification.vue";

const store = useStore();

const notifications = computed(
  () => store.getters["notifications/notifications"]
);
const hasNotifications = computed(
  () => store.getters["notifications/hasNotifications"]
);
</script>

<style scoped>
.notifications-badge {
  border-radius: 50%;
  background: var(--primary-color);
  height: 0.75rem;
  width: 0.75rem;
  font-size: 0.5rem;
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 3rem;
  /* todo: Add support for directly styling <Dropdown> container, resizing based on a child element such as header is lame */
  width: 400px;
}

.notifications-container {
  display: grid;
  gap: 0.5rem;
}

.notification {
  position: relative;
  border: 1px solid var(--border-color);
  border-radius: 15px;
  padding: 0.75rem 1.25rem;
  text-decoration: none;
  color: var(--primary-text-color);

  background: 0;
  text-align: left;
}
</style>
