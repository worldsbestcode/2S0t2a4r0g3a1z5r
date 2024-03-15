<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <StubsTable
      :data="endpointData?.credentials ?? []"
      description="In this menu, you can manage credentials and authentication materials for your application endpoints. Credentials might include passwords, API keys, and more. Search for existing credentials, add or delete credentials, and export to CSV."
      empty-message="No credentials found"
      :export-name="`${endpointData?.objInfo?.name}-credentials`"
      :headers="['Identity UUID', 'Created', 'Actions']"
      hide-pagination
      :loading="loading"
      :search-keys="['identityUuid']"
      title="Manage Credentials"
    >
      <template #addButton>
        <ClientAppEndpointCredentialCreate />
      </template>

      <template #tableRows="{ data }">
        <tr v-for="credential in data" :key="credential.identityUuid">
          <td>{{ credential.identityUuid }}</td>
          <td>{{ timestampToDate(credential.creationTime) }}</td>
          <td>
            <ClientAppEndpointCredentialDelete
              :credential-uuid="credential.identityUuid"
              :endpoint-uuid="endpointData.objInfo.uuid"
            />
          </td>
        </tr>
      </template>
    </StubsTable>
  </DeployedServiceWrapper>
</template>

<script setup>
import { computed, defineProps, inject } from "vue";
import { useRoute } from "vue-router";

import ClientAppEndpointCredentialCreate from "@/components/client-app/ClientAppEndpointCredentialCreate.vue";
import ClientAppEndpointCredentialDelete from "@/components/client-app/ClientAppEndpointCredentialDelete.vue";
import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import StubsTable from "@/components/StubsTable.vue";
import { timestampToDate } from "@/misc";

const route = useRoute();

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
});

const endpointData = inject("endpointData");

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "endpointCredentials",
        params: route.params,
      },
      name: "Credentials",
    },
  ];
});

const loading = computed(() => endpointData.value === null);
</script>
