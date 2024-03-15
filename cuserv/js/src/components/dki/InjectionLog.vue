<template>
  <div
    class="cover-screen"
    style="background: var(--secondary-background-color)"
  >
    <DeployedServiceHeader :crumbs="crumbs" />

    <StubsTable
      v-model:page="state.page"
      v-model:pageSize="state.pageSize"
      v-model:totalPages="state.totalPages"
      :data="state.logMessages"
      :export-name="`${state?.log?.objInfo?.name}-logs`"
      :search-keys="['Status', 'Date', 'Message']"
      empty-message="No messages found"
      title="Injection Log"
      :headers="['Date', 'Status', 'Message']"
    >
      <template #tableRows="{ data }">
        <tr v-for="(logMessage, index) in data" :key="index">
          <td>{{ logMessage.status }}</td>
          <td>{{ logMessage.timeStamp }}</td>
          <td>{{ logMessage.msg }}</td>
        </tr>
      </template>
    </StubsTable>
  </div>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, onBeforeMount, reactive } from "vue";
import { useRoute } from "vue-router";

import DeployedServiceHeader from "@/components/deploy-service/DeployedServiceHeader.vue";
import StubsTable from "@/components/StubsTable.vue";

const route = useRoute();

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
  serviceUuid: {
    type: String,
    required: true,
  },
  logUuid: {
    type: String,
    required: true,
  },
});

const state = reactive({
  logMessages: [],
  log: {},
  page: 0,
  totalPages: 1,
  pageSize: 15,
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: { name: "injectionLog", params: route.params },
      name: "Injection Log",
    },
  ];
});

onBeforeMount(() => {
  axios
    .get(`/dki/v1/logs/${props.logUuid}`, {
      errorContext: "Failed to fetch injection log",
    })
    .then((response) => {
      state.logMessages = response.data.logMessages;
      state.log = response.data;
    });
});
</script>
