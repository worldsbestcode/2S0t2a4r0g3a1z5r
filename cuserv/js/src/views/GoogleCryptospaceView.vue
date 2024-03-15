<template>
  <DeployedServiceWrapper :crumbs="crumbs" :loading="loading">
    <InformationAndActions
      description="CryptoSpaces are separate collections of encryption keys used with your Google services. From this menu, you can create view your keys and CryptoSpace information."
      :table-items="[
        ['Name', state.cryptospace?.objInfo?.name],
        ['Created', timestampToDate(state.cryptospace?.objInfo?.creationDate)],
        ['Service Accounts', serviceAccounts],
        ['Justifications', state?.cryptospace?.defaultJustifications],
      ]"
      :title="state?.cryptospace?.objInfo?.name ?? 'CryptoSpace'"
    >
      <template #actions>
        <GoogleCryptospaceEdit
          :cryptospace="state.cryptospace"
          :service-accounts="state.serviceAccounts"
        />
        <GoogleCryptospaceDelete
          :cryptospace-uuid="state?.cryptospace?.objInfo?.uuid"
          icon
        />
      </template>

      <template #tableRows>
        <UriTableRow
          name="CryptoSpace"
          :path="`/cryptospaces/${props.cryptospaceUuid}`"
        />
      </template>

      <RouterLink
        class="deployed-service-main__actions-link"
        :to="{ name: 'cryptospaceKeys' }"
      >
        <img
          class="deployed-service-main__actions-img"
          src="/shared/static/key.svg"
        />
        KEYS
      </RouterLink>
      <RouterLink
        class="deployed-service-main__actions-link"
        :to="{ name: 'cryptospaceLogs' }"
      >
        <img
          class="deployed-service-main__actions-img"
          src="/shared/static/folder-cloud.svg"
        />
        LOGS
      </RouterLink>
    </InformationAndActions>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, reactive, ref, watchEffect } from "vue";
import { useRoute } from "vue-router";

import { useBus } from "$shared/bus.js";

import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import GoogleCryptospaceDelete from "@/components/google-cryptospace/GoogleCryptospaceDelete.vue";
import GoogleCryptospaceEdit from "@/components/google-cryptospace/GoogleCryptospaceEdit.vue";
import UriTableRow from "@/components/google-cryptospace/UriTableRow.vue";
import InformationAndActions from "@/components/InformationAndActions.vue";
import { timestampToDate } from "@/misc.js";

const route = useRoute();

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
  cryptospaceUuid: {
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
  cryptospace: {},
  serviceAccounts: [],
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "cryptospace",
        params: route.params,
      },
      name: state?.cryptospace?.objInfo?.name ?? "CryptoSpace",
    },
  ];
});

const serviceAccounts = computed(() => {
  const serviceAccountUuidsWithPermissions =
    state.cryptospace?.accountPerms?.map(
      (permissions) => permissions.accountUuid,
    ) ?? [];

  const serviceAccountNamesWithPermissions =
    serviceAccountUuidsWithPermissions.map(
      (serviceAccountUuid) =>
        state.serviceAccounts.find(
          (serviceAccount) => serviceAccount.uuid === serviceAccountUuid,
        )?.name,
    );

  return serviceAccountNamesWithPermissions;
});

function fetchCryptospace() {
  axios
    .get(`/gekms/v1/cryptospaces/${props.cryptospaceUuid}`, {
      errorContext: "Failed to fetch CryptoSpace",
      loading,
    })
    .then((response) => {
      state.cryptospace = response.data;
    });
}

function fetchServiceAccounts() {
  axios
    .get(`/gekms/v1/accounts/${props.serviceUuid}`, {
      errorContext: "Failed to fetch Google Cloud service accounts",
      loading,
    })
    .then((response) => {
      state.serviceAccounts = response.data.accounts;
    });
}

function fetchResults() {
  fetchCryptospace();
  fetchServiceAccounts();
}

watchEffect(fetchResults);
useBus("updateCryptospace", fetchResults);
</script>
