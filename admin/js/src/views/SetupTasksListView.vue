<template>
  <div class="item-category">
    <div class="item-category__text" :title="props.tasksTypeText">
      {{ props.tasksTypeText }} Tasks
    </div>
    <div class="item-category__line" />
  </div>
  <div
    class="item-category__container"
    :class="props.listStyle === 'list' && 'item-category__container--list'"
  >
    <RouterLink
      v-for="link in notificationLinks"
      :key="link.routeName"
      :to="link.routeName"
      class="button-primary button-link"
    >
      {{ link.text }}
    </RouterLink>
  </div>

  <RouterView />
</template>

<script setup>
import { computed, defineProps, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";

import { adminSetups } from "$shared/admin.js";
import { listStyle as listStyleProp } from "$shared/props.js";

const route = useRoute();
const router = useRouter();
const store = useStore();

const props = defineProps({
  listStyle: listStyleProp,
  tasksTypeText: {
    type: String,
    required: true,
  },
  notificationsGetter: {
    type: String,
    required: true,
  },
});

const notifications = computed(() => store.getters[props.notificationsGetter]);

const notificationLinks = computed(() => {
  const ret = [];

  for (const adminSetup of adminSetups) {
    if (notifications.value.includes(adminSetup.type)) {
      ret.push({
        text: adminSetup.text,
        routeName: adminSetup.path,
      });
    }
  }

  return ret;
});

const hasPendingTasks = computed(
  () => store.getters["notifications/setupPending"].length > 0,
);

watchEffect(() => {
  if (route.name === "pending" && !hasPendingTasks.value) {
    router.replace({ name: "completed" });
  }
});
</script>
