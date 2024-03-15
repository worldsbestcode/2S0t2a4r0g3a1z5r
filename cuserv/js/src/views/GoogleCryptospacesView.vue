<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <StubsTable
      v-model:page="state.page"
      v-model:pageSize="state.pageSize"
      v-model:totalPages="state.totalPages"
      :data="state.results"
      :description="`CryptoSpaces are separate collections of encryption keys used with your Google services. From this menu, you can create new CryptoSpaces, determine which key management functions they fulfill, and manage or delete existing CryptoSpaces.

Click the CryptoSpaces below to view and manage its keys, or to add new ones to the group.`"
      empty-message="No CryptoSpaces found"
      :export-name="`${serviceData?.objInfo?.name}-cryptospaces`"
      :headers="['CryptoSpace name', 'Created', 'Actions']"
      :loading="loading"
      :search-keys="['objInfo.name']"
      title="Manage CryptoSpaces"
    >
      <template #addButton>
        <GoogleCryptospaceCreate v-bind="$attrs" />
      </template>
      <template #tableRows="{ data }">
        <tr
          v-for="cryptospace in data"
          :key="cryptospace.objInfo.uuid"
          style="cursor: pointer"
          @click="navigateCryptospace($event, cryptospace.objInfo.uuid)"
        >
          <td>
            {{ cryptospace.objInfo.name }}
          </td>
          <td>{{ timestampToDate(cryptospace.objInfo.creationDate) }}</td>
          <td>
            <GoogleCryptospaceDelete
              :cryptospace-uuid="cryptospace.objInfo.uuid"
              text
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

import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import GoogleCryptospaceCreate from "@/components/google-cryptospace/GoogleCryptospaceCreate.vue";
import GoogleCryptospaceDelete from "@/components/google-cryptospace/GoogleCryptospaceDelete.vue";
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
        name: "cryptospaces",
        params: route.params,
      },
      name: "CryptoSpaces",
    },
  ];
});

function navigateCryptospace(event, cryptospaceUuid) {
  if (event.target.tagName === "BUTTON") {
    return;
  }

  router.push({ name: "cryptospace", params: { cryptospaceUuid } });
}

function fetchResults() {
  axios
    .get("/gekms/v1/cryptospaces/stubs", {
      params: {
        page: state.page,
        pageSize: state.pageSize,
        service: props.serviceUuid,
      },
      errorContext: "Failed to fetch CryptoSpaces",
      loading,
    })
    .then((response) => {
      stubsSynchronize(response, state);
    });
}
watchEffect(fetchResults);
useBus("updateCryptospaces", fetchResults);
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
