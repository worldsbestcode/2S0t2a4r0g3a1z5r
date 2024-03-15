<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <StubsTable
      v-model:page="state.page"
      v-model:pageSize="state.pageSize"
      v-model:totalPages="state.totalPages"
      :data="state.results"
      :description="`Manage any encryption keys created for this CryptoSpace. Click Add New to specify an encryption algorithm and create a key. Click Delete to logically destroy keys.`"
      empty-message="No keys found"
      :export-name="`${serviceData?.objInfo?.name}-keys`"
      :headers="['Key name', 'Created', 'Last Used', 'Actions']"
      :loading="loading"
      :search-keys="['objInfo.name']"
      title="Manage Keys"
    >
      <template #addButton>
        <GoogleCryptospaceKeyCreate v-bind="$attrs" />
      </template>
      <template #tableRows="{ data }">
        <tr
          v-for="key in data"
          :key="key.objInfo.uuid"
          style="cursor: pointer"
          @click="navigateKey($event, key.objInfo.uuid)"
        >
          <td>
            {{ key.objInfo.name }}
          </td>
          <td>{{ timestampToDate(key.objInfo.creationDate) }}</td>
          <td>{{ timestampToDate(key.lastUsed) }}</td>
          <td>
            <GoogleCryptospaceKeyDelete text :key-uuid="key.objInfo.uuid" />
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
import GoogleCryptospaceKeyCreate from "@/components/google-cryptospace/GoogleCryptospaceKeyCreate.vue";
import GoogleCryptospaceKeyDelete from "@/components/google-cryptospace/GoogleCryptospaceKeyDelete.vue";
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
  cryptospaceUuid: {
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
        name: "cryptospaceKeys",
        params: route.params,
      },
      name: "Keys",
    },
  ];
});

function navigateKey(event, keyUuid) {
  if (event.target.tagName === "BUTTON") {
    return;
  }

  router.push({ name: "cryptospaceKey", params: { keyUuid } });
}

function fetchResults() {
  axios
    .get("/gekms/v1/keys/stubs", {
      params: {
        page: state.page,
        pageSize: state.pageSize,
        cryptoSpace: props.cryptospaceUuid,
      },
      errorContext: "Failed to fetch keys",
      loading,
    })
    .then((response) => {
      stubsSynchronize(response, state);
    });
}
watchEffect(fetchResults);
useBus("updateCryptospaceKeys", fetchResults);
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
