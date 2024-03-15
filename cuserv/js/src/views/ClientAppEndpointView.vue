<template>
  <DeployedServiceWrapper :crumbs="crumbs" :loading="loading">
    <InformationAndActions
      description="This menu displays information about the endpoint via which your client application communicates with CryptoHub. You can manage endpoint credentials and authentication material in the Actions menu below."
      :table-items="[
        ['Name', endpointName],
        ['Created', timestampToDate(endpointData?.objInfo?.creationDate)],
        ['Endpoint', endpointData?.endpointName],
        ['AuthType', endpointData?.authType],
        ['Platform', endpointData?.platform],
        ['CryptoHub Hostname', endpointData?.deviceAddress],
      ]"
      :title="endpointName"
    >
      <template #actions>
        <ClientAppEndpointDelete
          icon
          :endpoint-uuid="endpointUuid"
          @finished="$router.replace(crumbs[crumbs.length - 2].to)"
        />
      </template>

      <!-- todo: make component for actions link compatible with modal opener button -->
      <RouterLink
        class="deployed-service-main__actions-link"
        :to="{ name: 'endpointCredentials' }"
      >
        <img
          class="deployed-service-main__actions-img"
          src="/shared/static/key.svg"
        />
        CREDENTIALS
      </RouterLink>

      <ClientAppEndpointDelete
        action
        :endpoint-uuid="endpointUuid"
        @finished="$router.replace(crumbs[crumbs.length - 2].to)"
      />
    </InformationAndActions>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, provide, ref, watchEffect } from "vue";
import { useRoute } from "vue-router";

import { useBus } from "$shared/bus.js";

import ClientAppEndpointDelete from "@/components/client-app/ClientAppEndpointDelete.vue";
import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import InformationAndActions from "@/components/InformationAndActions.vue";
import { timestampToDate } from "@/misc";

const route = useRoute();

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
});

const loading = ref(false);
const endpointData = ref(null);
provide("endpointData", endpointData);

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "endpoint",
        params: route.params,
      },
      name: endpointName.value,
    },
  ];
});

const endpointUuid = computed(() => route.params.endpointUuid);

const endpointName = computed(
  () => endpointData.value?.objInfo?.name ?? "Endpoint",
);

function fetchResults() {
  // Prevent fetchResults from firing when navigating back to manage endpoints view
  if (!endpointUuid.value) {
    return;
  }
  axios
    .get(`/cuserv/v1/clientapp/endpoint/${endpointUuid.value}`, {
      errorContext: "Failed to fetch endpoint",
      loading,
    })
    .then((response) => {
      endpointData.value = response.data;
    });
}
watchEffect(fetchResults);
useBus("updateEndpoint", fetchResults);
</script>
