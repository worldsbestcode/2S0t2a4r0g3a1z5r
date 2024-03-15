<template>
  <div class="fx-pedinject">
    <div class="fx-pedinject__header">
      <fx-inject-header :service-id="serviceUuid"></fx-inject-header>
    </div>

    <fx-bread-crumbs :serviceUuid="serviceUuid" />
    <div v-if="sessionExpired" class="fx-pedinject__expired">
      <fx-label class="mx-2 my-3" text="Your session has expired" />

      <v-progress-circular
        v-if="waitingForNewSession"
        class="fx-progress"
        indeterminate
        color="var(--primary-color)"
      />
      <fx-button v-else text="START NEW SESSION" @click="startNewSession" />
    </div>
    <div v-else class="fx-pedinject__service">
      <div class="fx-pedinject__slots">
        <fx-controls></fx-controls>
        <fx-slots></fx-slots>
        <fx-pagination
          v-model:page="page"
          v-model:pageSize="pageSize"
          :total-pages="totalPages"
        ></fx-pagination>
      </div>
      <div class="fx-pedinject__log">
        <fx-log-follower></fx-log-follower>
      </div>
    </div>
  </div>
  <v-dialog v-model="sessionExpiring" max-width="700px" :persistent="true">
    <fx-expiring-session />
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch, watchEffect } from "vue";
import { useRoute } from "vue-router";
import { querySession } from "../utils/common.js";
import FxBreadCrumbs from "@/components/FXBreadCrumbs.vue";
import FxSlots from "@/components/FXSlots.vue";
import FxControls from "@/components/FXControls.vue";
import FxPagination from "@/components/FXPagination.vue";
import FxInjectHeader from "@/components/FXInjectHeader.vue";
import FxLogFollower from "@/components/FXLogFollower.vue";
import FxExpiringSession from "@/components/FXExpiringSession.vue";

import store from "@/store";

const EXPIRING_TIMEOUT_MS = 1000; // one second
const CHECK_REMAINING_TIME_TIMEOUT_MS = 5000; // five seconds
const SESSION_EXPIRING_THRESHOLD_SEC = 120; // two minutes
const QUERY_SLOTS_MS = 7000; // seven seconds
const route = useRoute();

let timerId = null;
let slotsTimer = null;
// TODO (DR) - move these values to the store
let devices = computed(() => {
  return store.getters["pedinject/getDevices"];
});

// TODO (DR) - remove these.
const page = computed({
  get() {
    return store.getters["pedinject/getPagination"].page;
  },
  set(value) {
    let pagination = store.getters["pedinject/getPagination"];

    pagination.page = value;

    store.dispatch("pedinject/setPagination", pagination);
  },
});

const waitingForNewSession = ref(false);

const sessionExpired = computed(
  () => store.getters["serviceInfo/getRemainingTime"] === 0,
);

const sessionExpiring = computed(() => {
  let remainingTime = store.getters["serviceInfo/getRemainingTime"];

  return remainingTime < SESSION_EXPIRING_THRESHOLD_SEC && remainingTime > 0;
});

const pageSize = computed({
  get() {
    return store.getters["pedinject/getPagination"].pageSize;
  },
  set(value) {
    let pagination = store.getters["pedinject/getPagination"];
    pagination.pageSize = value;
    store.dispatch("pedinject/setPagination", pagination);
  },
});

watch(pageSize, () => {
  let totalPages = Math.ceil(devices.value.length / pageSize.value);
  let pagination = store.getters["pedinject/getPagination"];
  pagination.totalPages = totalPages;
  store.dispatch("pedinject/setPagination", pagination);
});

watch(devices, () => {
  let totalPages = Math.ceil(devices.value.length / pageSize.value);
  let pagination = store.getters["pedinject/getPagination"];
  pagination.totalPages = totalPages;
  store.dispatch("pedinject/setPagination", pagination);
});

const totalPages = computed(() => {
  return store.getters["pedinject/getPagination"].totalPages;
});

const serviceUuid = route.params.service_id;
const deviceGroupUuid = computed(() => {
  return store.getters["serviceInfo/getDeviceGroupUuid"];
});

const sessionUuid = computed(() => {
  return store.getters["pedinject/getSessionId"];
});

const querySessionCallback = async () => {
  querySession(sessionUuid.value, false);
};

watch(
  sessionUuid,
  () => {
    if (slotsTimer === null) {
      store.dispatch("pedinject/getSlots", sessionUuid.value);

      slotsTimer = setInterval(() => {
        store.dispatch("pedinject/getSlots", sessionUuid.value);
      }, QUERY_SLOTS_MS);
    }
    if (timerId === null) {
      timerId = setInterval(
        querySessionCallback,
        CHECK_REMAINING_TIME_TIMEOUT_MS,
      );
    }

    waitingForNewSession.value = false;
    store.dispatch("serviceInfo/resetSession");
  },
  { eager: true },
);

watch(sessionExpiring, () => {
  if (timerId) {
    clearInterval(timerId);
    clearInterval(slotsTimer);
    timerId = null;
    slotsTimer = null;
  }

  let timeout = CHECK_REMAINING_TIME_TIMEOUT_MS;
  if (sessionExpiring.value) {
    timeout = EXPIRING_TIMEOUT_MS;
  }
  timerId = setInterval(querySessionCallback, timeout);
});

watch(deviceGroupUuid, () => {
  const startSessionParams = {
    device_group: deviceGroupUuid.value,
    service_id: serviceUuid,
  };
  store.dispatch("pedinject/startSession", startSessionParams);
});

watchEffect(() => {
  store.dispatch("pedinject/setServiceId", serviceUuid);
  store.dispatch("serviceInfo/queryInfo", serviceUuid);
});

const startNewSession = () => {
  const startSessionParams = {
    device_group: deviceGroupUuid.value,
    service_id: serviceUuid,
  };
  waitingForNewSession.value = true;
  store.dispatch("pedinject/startSession", startSessionParams);
};
</script>

<style scoped>
.fx-pedinject {
  width: 100%;
  background-color: var(--secondary-background-color);
}

.fx-pedinject__header {
  width: 100%;
}
.fx-pedinject__service {
  display: flex;
  background-color: var(--secondary-background-color);
  padding: 2rem 16rem;
  justify-content: space-between;
  height: inherit;
}

.fx-pedinject__expired {
  display: block;
  flex-wrap: wrap;
  padding: 5rem 0rem;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}

.fx-progress {
  display: flex;
  margin-left: auto;
  margin-right: auto;
}

.fx-pedinject__slots {
  display: blocks;
  min-width: 60%;
}

.fx-pedinject__log {
  display: blocks;
  margin-left: 3rem;
}
</style>
