<template>
  <main class="app-main chc-main-horizontal-padding">
    <h1 class="service-management-text" title="Administration Tasks">
      Administration Tasks
    </h1>

    <div class="service-management-actions-container">
      <div class="service-management-actions">
        <ChcMainRouterLink v-if="hasPendingTasks" :to="{ name: 'pending' }">
          Pending
        </ChcMainRouterLink>
        <ChcMainRouterLink v-if="hasCompletedTasks" :to="{ name: 'completed' }">
          Completed
        </ChcMainRouterLink>
        <ChcMainRouterLink :to="{ name: 'settings' }">
          Settings
        </ChcMainRouterLink>
      </div>
      <div class="service-management-actions">
        <RouterLink
          v-if="hasPendingTasks"
          :to="{ name: 'setup' }"
          class="chc-main-link"
        >
          Finish Setup
        </RouterLink>

        <ChcListStyle v-model="state.listStyle" />
      </div>
    </div>

    <ChcHorizontalSeperator />

    <RouterView :list-style="state.listStyle" />
  </main>
</template>

<script setup>
import { computed, reactive, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";

import ChcHorizontalSeperator from "$shared/components/ChcHorizontalSeperator.vue";
import ChcListStyle from "$shared/components/ChcListStyle.vue";
import ChcMainRouterLink from "$shared/components/ChcMainRouterLink.vue";

const route = useRoute();
const router = useRouter();
const store = useStore();

const state = reactive({
  listStyle: "tile",
});

const hasPendingTasks = computed(
  () => store.getters["notifications/setupPending"].length > 0,
);

const hasCompletedTasks = computed(
  () => store.getters["notifications/setupCompleted"].length > 0,
);

watchEffect(() => {
  if (route.name === "landing") {
    if (hasPendingTasks.value) {
      router.replace({ name: "pending" });
    } else {
      router.replace({ name: "completed" });
    }
  }
});
</script>
