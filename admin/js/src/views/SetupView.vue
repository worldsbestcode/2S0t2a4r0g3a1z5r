<template>
  <div class="cover-screen">
    <RouterBreadCrumbs seperator :crumbs="crumbs" />

    <component :is="pathInformation?.[route.params.setupPath]?.component" />
  </div>
</template>

<script setup>
import { computed, provide } from "vue";
import { useRoute } from "vue-router";

import RouterBreadCrumbs from "$shared/components/RouterBreadCrumbs.vue";
import { useCrumbs } from "$shared/composables.js";

import TaskAutomaticBackups from "@/components/tasks/TaskAutomaticBackups.vue";
import TaskDateTime from "@/components/tasks/TaskDateTime.vue";
import TaskJoinCluster from "@/components/tasks/TaskJoinCluster.vue";
import TaskLicense from "@/components/tasks/TaskLicense.vue";
import TaskMajorKeys from "@/components/tasks/TaskMajorKeys.vue";
import TaskNetworking from "@/components/tasks/TaskNetworking.vue";
import TaskSecureMode from "@/components/tasks/TaskSecureMode.vue";

const route = useRoute();

const pathInformation = {
  license: {
    crumb: "License",
    component: TaskLicense,
  },
  secure: {
    crumb: "Secure Mode",
    component: TaskSecureMode,
  },
  major: {
    crumb: "Major Keys",
    component: TaskMajorKeys,
  },
  networking: {
    crumb: "Networking",
    component: TaskNetworking,
  },
  date: {
    crumb: "Date & Time",
    component: TaskDateTime,
  },
  automatic: {
    crumb: "Automatic Backups",
    component: TaskAutomaticBackups,
  },
  join: {
    crumb: "Join Clusters",
    component: TaskJoinCluster,
  },
};

const crumbs = computed(() => {
  const metaCrumbs = useCrumbs().value;
  metaCrumbs.pop();
  metaCrumbs.push({
    name: pathInformation?.[route.params.setupPath]?.crumb,
    to: {
      path: route.path,
    },
  });
  return metaCrumbs;
});

provide("previousPage", undefined);
provide("nextPage", undefined);
provide("skip", undefined);
</script>
