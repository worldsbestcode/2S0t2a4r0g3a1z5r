<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <StubsTable
      v-model:page="state.page"
      v-model:pageSize="state.pageSize"
      v-model:totalPages="state.totalPages"
      :data="state.results"
      :description="`Encryption keys are used by the client application to process cryptographic operations. In this menu, you may manage encryption keys. You may create keys according to specific encryption algorithms or delete them entirely.`"
      empty-message="No keys found"
      :export-name="`${serviceData?.objInfo?.name}-keys`"
      :headers="['Name', 'Key Type', 'Key Usage', 'Created', 'Expiration']"
      :loading="loading"
      :search-keys="['name, keyType, keyUsage']"
      title="Manage Keys"
    >
      <template #tableRows="{ data }">
        <tr v-for="key in data" :key="key.uuid">
          <td>{{ key.name }}</td>
          <td>{{ key.keyType }}</td>
          <td>{{ key.keyUsage }}</td>
          <td>{{ timestampToDate(key.created) }}</td>
          <td>{{ timestampToDate(key.expiration) }}</td>
        </tr>
      </template>
    </StubsTable>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, inject, reactive, ref, watchEffect } from "vue";
import { useRoute } from "vue-router";

import { useBus } from "$shared/bus.js";

import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import StubsTable from "@/components/StubsTable.vue";
import { stubsSynchronize, timestampToDate } from "@/misc.js";

const route = useRoute();

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
        name: "clientAppKeys",
        params: route.params,
      },
      name: "Keys",
    },
  ];
});

function fetchResults() {
  axios
    .get(`/cuserv/v1/clientapp/keys`, {
      params: {
        page: state.page,
        pageSize: state.pageSize,
        service: props.serviceUuid,
      },
      errorContext: "Failed to fetch keys",
      loading,
    })
    .then((response) => {
      stubsSynchronize(response, state);
    });
}

watchEffect(fetchResults);
useBus("updateEndpointKeys", fetchResults);
</script>
