<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <StubsTable
      v-model:page="state.page"
      v-model:pageSize="state.pageSize"
      v-model:totalPages="state.totalPages"
      :data="state.results"
      :description="`Endpoints refer to devices that are authorized to access this service. In this menu, you can view and filter details about existing endpoints. You can also add new endpoints by clicking the Add New button. This will prompt you to enter the device address and specify the endpoint.`"
      empty-message="No endpoints found"
      :export-name="`${serviceData?.objInfo?.name}-endpoints`"
      :headers="['Endpoint Name', 'Endpoint Type', 'Created', 'Actions']"
      :loading="loading"
      :search-keys="['objInfo.name', 'endpointName']"
      title="Manage Endpoints"
    >
      <template #addButton>
        <ClientAppEndpointsCreate v-bind="$attrs" />
      </template>

      <template #tableRows="{ data }">
        <tr
          v-for="endpoint in data"
          :key="endpoint.objInfo.uuid"
          style="cursor: pointer"
          @click="navigateEndpoint($event, endpoint.objInfo.uuid)"
        >
          <td>
            {{ endpoint.objInfo.name }}
          </td>
          <td>{{ endpoint.endpointName }}</td>
          <td>{{ timestampToDate(endpoint.objInfo.creationDate) }}</td>
          <td>
            <ClientAppEndpointDelete
              text
              :endpoint-uuid="endpoint.objInfo.uuid"
            />
          </td>
        </tr>
      </template>
    </StubsTable>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, inject, reactive, ref, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useBus } from "$shared/bus.js";

import ClientAppEndpointsCreate from "@/components/client-app/ClientAppEndpointCreate.vue";
import ClientAppEndpointDelete from "@/components/client-app/ClientAppEndpointDelete.vue";
import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import StubsTable from "@/components/StubsTable.vue";
import { stubsSynchronize, timestampToDate } from "@/misc.js";

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

const state = reactive({
  page: 1,
  pageSize: 5,
  totalPages: 1,
  results: [],
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "endpoints",
        params: route.params,
      },
      name: "Endpoints",
    },
  ];
});

function navigateEndpoint(event, endpointUuid) {
  if (event.target.tagName === "BUTTON") {
    return;
  }

  router.push({ name: "endpoint", params: { endpointUuid } });
}

function fetchResults() {
  axios
    .get("/cuserv/v1/clientapp/endpoint/stubs", {
      params: {
        page: state.page,
        pageSize: state.pageSize,
        service: props.serviceUuid,
      },
      errorContext: "Failed to fetch endpoints",
      loading,
    })
    .then((response) => {
      stubsSynchronize(response, state);
    });
}
watchEffect(fetchResults);
useBus("updateEndpoints", fetchResults);
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
