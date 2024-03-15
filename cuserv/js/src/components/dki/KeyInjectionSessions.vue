<template>
  <div
    class="cover-screen"
    style="background: var(--secondary-background-color)"
  >
    <DeployedServiceHeader :crumbs="crumbs" />

    <StubsTable
      v-model:page="pagination.page"
      v-model:pageSize="pagination.pageSize"
      v-model:totalPages="pagination.totalPages"
      :data="pagination.results"
      :description="`This page shows all the key loading sessions. Each key loading session represents a specific period in  which devices were loaded.`"
      empty-message="No injection sessions found"
      :export-name="`${serviceData?.objInfo?.name}-logs`"
      :headers="[
        'Start Time',
        'Users',
        '# Devices Loaded',
        '# Keys Loaded',
        'Actions',
      ]"
      :loading="loading"
      :search-keys="['logType', 'Time']"
      title="Key Loading Sessions"
    >
      <template #tableRows="{ data }">
        <tr v-for="log in data" :key="log.oid">
          <td>{{ unixDateToString(log.startTime) }}</td>
          <td>{{ log.users }}</td>
          <td>{{ getNumberOfLoadedDevices(log.objInfo.uuid) }}</td>
          <td>{{ getNumberOfLoadedKey(log.objInfo.uuid) }}</td>
          <td>
            <ChcTooltipButtonIcon
              class="table__link"
              icon="point_of_sale"
              tooltip="View Devices"
              @click="viewDeviceLoadingEvents(log)"
            />
          </td>
        </tr>
      </template>
    </StubsTable>
  </div>

  <RouterView :crumbs="crumbs" :service-uuid="props.serviceUuid" />
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, inject, reactive, ref, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";

import ChcTooltipButtonIcon from "$shared/components/ChcTooltipButtonIcon.vue";

import DeployedServiceHeader from "@/components/deploy-service/DeployedServiceHeader.vue";
import StubsTable from "@/components/StubsTable.vue";

const route = useRoute();
const router = useRouter();

const serviceData = inject("serviceData");

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
  serviceUuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

const pagination = reactive({
  page: 1,
  pageSize: 15,
  totalPages: 1,
  results: [],
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "keyInjectionSessions",
        params: route.params,
      },
      name: "Key Injection Sessions",
    },
  ];
});

let logDeviceMap = new Map();
const unixDateToString = (unixDate) => {
  const date = new Date(unixDate * 1000);
  return date.toLocaleString();
};

const viewDeviceLoadingEvents = (log) => {
  router.push({
    name: "deviceLoadingEvents",
    params: {
      sessionUuid: log.objInfo.uuid,
    },
  });
};

async function fetchLogData(log) {
  axios
    .get(`/dki/v1/logs/info/${log.objInfo.uuid}`, {
      errorContext: "Failed to get log info",
      loading,
    })
    .then((response) => {
      if (response.data.totalDevicesLoaded > 0) {
        logDeviceMap.set(response.data.sessionUuid, {
          totalDevicesLoaded: response.data.totalDevicesLoaded,
          totalKeysLoaded: response.data.totalKeysLoaded,
        });
        pagination.results.push(log);
      }
    });
}

function fetchResults() {
  axios
    .get("/dki/v1/session/stubs", {
      params: {
        service_uuid: props.serviceUuid,
        page: pagination.page,
        pageSize: pagination.pageSize,
      },
      errorContxt: "Failed to query injection sessions",
      loading,
    })
    .then((response) => {
      response.data.results.forEach((result) => {
        fetchLogData(result);
      });
      pagination.totalPages = response.data.totalPages;
      pagination.page = response.data.previousPage;
    });
}

function getNumberOfLoadedDevices(uuid) {
  let totalDevicesLoaded = 0;
  let logInfo = logDeviceMap.get(uuid);

  if (logInfo) {
    totalDevicesLoaded = logInfo.totalDevicesLoaded;
  }
  return totalDevicesLoaded;
}

function getNumberOfLoadedKey(uuid) {
  let totalKeysLoaded = 0;
  let logInfo = logDeviceMap.get(uuid);

  if (logInfo) {
    totalKeysLoaded = logInfo.totalKeysLoaded;
  }
  return totalKeysLoaded;
}
watchEffect(() => {
  fetchResults();
});
</script>

<style scoped>
.deployed-manage-table .table__link {
  border: 0;
  padding: 0;
  background: 0;
  font-weight: initial;
  color: var(--primary-text-color);
}
.deployed-manage-table tbody tr:hover .table__link {
  color: var(--primary-color);
  text-decoration: underline;
}
</style>
