<template>
  <div class="cover-screen">
    <RouterBreadCrumbs seperator />

    <component :is="currentView" />
  </div>
</template>

<script setup>
import { computed, markRaw, provide, reactive, watchEffect } from "vue";
import { useStore } from "vuex";

import { adminSetupsOrder } from "$shared/admin.js";
import RouterBreadCrumbs from "$shared/components/RouterBreadCrumbs.vue";

import TaskAutomaticBackups from "@/components/tasks/TaskAutomaticBackups.vue";
import TaskDateTime from "@/components/tasks/TaskDateTime.vue";
import TaskJoinCluster from "@/components/tasks/TaskJoinCluster.vue";
import TaskLicense from "@/components/tasks/TaskLicense.vue";
import TaskMajorKeys from "@/components/tasks/TaskMajorKeys.vue";
import TaskNetworking from "@/components/tasks/TaskNetworking.vue";
import TaskSecureMode from "@/components/tasks/TaskSecureMode.vue";

const store = useStore();

const setupTypeViews = {
  License: TaskLicense,
  SecureMode: TaskSecureMode,
  MajorKeys: TaskMajorKeys,
  Networking: TaskNetworking,
  DateTime: TaskDateTime,
  AutomaticBackups: TaskAutomaticBackups,
  JoinCluster: TaskJoinCluster,
};

const viewSetupTypes = new WeakMap();
for (const [type, view] of Object.entries(setupTypeViews)) {
  viewSetupTypes.set(view, type);
}

const state = reactive({
  viewIndex: 0,
  setupPendingViews: [],
});

const setupPending = computed(
  () => store.getters["notifications/setupPending"],
);

const currentView = computed(() => state.setupPendingViews[state.viewIndex]);

const previousPage = computed(() => {
  if (state.viewIndex === 0) {
    return undefined;
  } else {
    return previousPageFunction;
  }
});

function previousPageFunction() {
  state.viewIndex--;
}

function nextPage() {
  state.viewIndex++;
}

function skip() {
  store.dispatch(
    "notifications/deleteSetupNotification",
    viewSetupTypes.get(currentView.value),
  );
  nextPage();
}

function initializeSetupPendingViews() {
  const setupPendingOrdered = adminSetupsOrder.filter((x) =>
    setupPending.value.includes(x),
  );

  state.setupPendingViews = setupPendingOrdered.map((x) =>
    markRaw(setupTypeViews[x]),
  );
}

provide("previousPage", previousPage);
provide("nextPage", nextPage);
provide("skip", skip);

initializeSetupPendingViews();

watchEffect(() => {
  if (!currentView.value) {
    window.location.href = "/cuserv";
  }
});
</script>
