<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <StubsTable
      v-model:page="state.page"
      v-model:totalPages="state.totalPages"
      v-model:pageSize="state.pageSize"
      title="Manage Keys"
      :description="`Manage any encryption keys created for this User. Click Add New to create a key and expire all other active keys. Click Delete to destroy keys.`"
      :headers="['Key name', 'Checksum', 'Expiration', 'Actions']"
      empty-message="No keys found"
      :loading="loading"
      :data="state.results"
      :search-keys="['name']"
      :export-name="`${serviceData?.objInfo?.name}-keys`"
    >
      <template #addButton>
        <GooglePersonalKeyCreate
          v-bind="$attrs"
          :service-uuid="props.serviceUuid"
          :email="props.email"
        />
      </template>
      <template #tableRows="{ data }">
        <tr
          v-for="key in data"
          :key="key.uuid"
          style="cursor: pointer"
          @click="navigateKey($event, key.uuid)"
        >
          <td>
            {{ key.name }}
          </td>
          <td>{{ key.checksum }}</td>
          <td>{{ key.endValidity }}</td>
          <td>
            <GooglePersonalKeyDelete
              text
              :service-uuid="props.serviceUuid"
              :email="props.email"
              :key-uuid="key.uuid"
            />
          </td>
        </tr>
      </template>
    </StubsTable>

    <template #routerView>
      <RouterView
        :crumbs="crumbs"
        :service-uuid="props.serviceUuid"
        :email="props.email"
      />
    </template>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, inject, reactive, ref, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useBus } from "$shared/bus.js";

import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import GooglePersonalKeyCreate from "@/components/google-user/GooglePersonalKeyCreate.vue";
import GooglePersonalKeyDelete from "@/components/google-user/GooglePersonalKeyDelete.vue";
import StubsTable from "@/components/StubsTable.vue";
import { stubsSynchronize } from "@/misc.js";

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
  email: {
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
        name: "personalKeys",
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

  router.push({ name: "personalKey", params: { keyUuid } });
}

function fetchResults() {
  if (!props.email) return;

  axios
    .get("/gcse/v1/keys", {
      params: {
        page: state.page,
        pageSize: state.pageSize,
        service: props.serviceUuid,
        email: props.email,
      },
      errorContext: "Failed to fetch keys",
      loading,
    })
    .then((response) => {
      stubsSynchronize(response, state);
    });
}
watchEffect(fetchResults);
useBus("updatePersonalKeys", fetchResults);
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
