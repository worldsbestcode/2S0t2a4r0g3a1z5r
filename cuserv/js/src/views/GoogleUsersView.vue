<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <StubsTable
      v-model:page="state.page"
      v-model:totalPages="state.totalPages"
      v-model:pageSize="state.pageSize"
      title="Manage Users"
      :description="`From this menu, you can create new Users, determine which key management functions they fulfill, and manage or delete existing Users.

Click the Users below to view and manage its keys, or to add new ones to the group.`"
      :headers="['User name', 'Created', 'Actions']"
      empty-message="No Users found"
      :loading="loading"
      :data="state.results"
      :search-keys="['objInfo.name']"
      :export-name="`${serviceData?.objInfo?.name}-users`"
    >
      <template #addButton>
        <GoogleUserCreate v-bind="$attrs" />
      </template>
      <template #tableRows="{ data }">
        <tr
          v-for="user in data"
          :key="user.objInfo.uuid"
          style="cursor: pointer"
          @click="navigateUser($event, user.objInfo.uuid)"
        >
          <td>
            {{ user.objInfo.name }}
          </td>
          <td>{{ timestampToDate(user.objInfo.creationDate) }}</td>
          <td>
            <GoogleUserDelete text :user-uuid="user.objInfo.uuid" />
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
import GoogleUserCreate from "@/components/google-user/GoogleUserCreate.vue";
import GoogleUserDelete from "@/components/google-user/GoogleUserDelete.vue";
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
        name: "googleUsers",
        params: route.params,
      },
      name: "Users",
    },
  ];
});

function navigateUser(event, userUuid) {
  if (event.target.tagName === "BUTTON") {
    return;
  }

  router.push({ name: "googleUser", params: { userUuid } });
}

function fetchResults() {
  axios
    .get("/gcse/v1/users/stubs", {
      params: {
        page: state.page,
        pageSize: state.pageSize,
        service: props.serviceUuid,
      },
      errorContext: "Failed to fetch Users",
      loading,
    })
    .then((response) => {
      stubsSynchronize(response, state);
    });
}
watchEffect(fetchResults);
useBus("updateUsers", fetchResults);
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
