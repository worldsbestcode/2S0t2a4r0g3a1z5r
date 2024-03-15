<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <StubsTable
      :data="state.results"
      description="Manage Google Cloud service accounts authorized to use the external key management system."
      empty-message="No Google Cloud service accounts found"
      :export-name="`${serviceData?.objInfo?.name}-service-accounts`"
      :headers="['Service Account', 'Actions']"
      hide-pagination
      :loading="loading"
      :search-keys="['uuid']"
      title="Manage Google Cloud Service Accounts"
    >
      <template #addButton>
        <ServiceAccountCreate :service-uuid="props.serviceUuid" />
      </template>
      <template #tableRows="{ data }">
        <tr v-for="serviceAccount in data" :key="serviceAccount.uuid">
          <td>{{ serviceAccount.name }}</td>
          <td>
            <ServiceAccountDelete
              :service-account-name="serviceAccount.name"
              :service-uuid="props.serviceUuid"
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
import { useRoute } from "vue-router";

import { useBus } from "$shared/bus.js";

import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import ServiceAccountCreate from "@/components/google/ServiceAccountCreate.vue";
import ServiceAccountDelete from "@/components/google/ServiceAccountDelete.vue";
import StubsTable from "@/components/StubsTable.vue";

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
  totalPages: 1,
  results: [],
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "serviceAccounts",
        params: route.params,
      },
      name: "Google Cloud Service Accounts",
    },
  ];
});

function fetchResults() {
  axios
    .get(`/gekms/v1/accounts/${props.serviceUuid}`, {
      errorContext: "Failed to fetch Google Cloud service accounts",
      loading,
    })
    .then((response) => {
      state.results = response.data.accounts;
    });
}

watchEffect(fetchResults);
useBus("updateServiceAccounts", fetchResults);
</script>
