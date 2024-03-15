<template>
  <DeployedServiceWrapper :crumbs="crumbs" :loading="loading">
    <InformationAndActions
      :title="state?.user?.objInfo?.name ?? 'User'"
      description="From this menu, you can view your keys and User information."
      :table-items="[
        ['Name', state.user?.objInfo?.name],
        ['Created', timestampToDate(state.user?.objInfo?.creationDate)],
        ['Email', state.user?.email],
        ['Enabled', state.user?.whitelisted ? 'Yes' : 'No'],
      ]"
    >
      <template #actions>
        <GoogleUserEdit :user="state?.user" />
        <GoogleUserDelete icon :user-uuid="state?.user?.objInfo?.uuid" />
      </template>

      <RouterLink
        :to="{ name: 'personalKeys' }"
        class="deployed-service-main__actions-link"
      >
        <img
          src="/shared/static/key.svg"
          class="deployed-service-main__actions-img"
        />
        KEYS
      </RouterLink>
      <RouterLink
        :to="{ name: 'userLogs' }"
        class="deployed-service-main__actions-link"
      >
        <img
          src="/shared/static/folder-cloud.svg"
          class="deployed-service-main__actions-img"
        />
        LOGS
      </RouterLink>
    </InformationAndActions>

    <template #routerView>
      <RouterView :crumbs="crumbs" :email="state.user.email" />
    </template>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, reactive, ref, watchEffect } from "vue";
import { useRoute } from "vue-router";

import { useBus } from "$shared/bus.js";

import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import GoogleUserDelete from "@/components/google-user/GoogleUserDelete.vue";
import GoogleUserEdit from "@/components/google-user/GoogleUserEdit.vue";
import InformationAndActions from "@/components/InformationAndActions.vue";
import { timestampToDate } from "@/misc.js";

const route = useRoute();

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
  userUuid: {
    type: String,
    required: true,
  },
  serviceUuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  user: {},
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "googleUser",
        params: route.params,
      },
      name: state?.user?.objInfo?.name ?? "User",
    },
  ];
});

function fetchResults() {
  axios
    .get(`/gcse/v1/users/${props.userUuid}`, {
      errorContext: "Failed to fetch User",
      loading,
    })
    .then((response) => {
      state.user = response.data;
    });
}

watchEffect(fetchResults);
useBus("updateUser", fetchResults);
</script>
