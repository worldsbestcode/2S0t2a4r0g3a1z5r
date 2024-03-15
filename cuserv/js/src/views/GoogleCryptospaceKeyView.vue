<template>
  <DeployedServiceWrapper :crumbs="crumbs" :loading="loading">
    <InformationAndActions
      description="CryptoHub is the most flexible and versatile cryptographic platform in the industry. It combines every cryptographic function within Futurex's extensive solution suite.

Users operate CryptoHub with a simple web dashboard to deploy virtual cryptographic modules to fulfill nearly any use case CryptoHub is the most flexible and versatile cryptographic platform in the industry. It combines every cryptographic function within Futurex's extensive solution suite."
      :table-items="[
        ['Name', state.key?.objInfo?.name],
        ['Created', timestampToDate(state.key?.objInfo?.creationDate)],
        ['Last Used', timestampToDate(state.key?.lastUsed)],
        ['Algorithm', state.key?.algorithm],
        ['Justifications', state.key?.justifications],
      ]"
      :title="state.key?.objInfo?.name ?? 'Key'"
    >
      <template #actions>
        <GoogleCryptospaceKeyEdit :key-information="state.key" />
        <GoogleCryptospaceKeyDelete
          icon
          :key-uuid="props.keyUuid"
          @finished="$router.replace(crumbs[crumbs.length - 2].to)"
        />
      </template>
      <template #tableRows>
        <UriTableRow name="Key" :path="`/keys/${props.keyUuid}`" />

        <tr v-if="state.key?.resourceName">
          <th>Resource Name</th>
          <td>{{ state.key.resourceName }}</td>
        </tr>
      </template>

      <RouterLink
        class="deployed-service-main__actions-link"
        :to="{ name: 'cryptospaceKeyLogs' }"
      >
        <img
          class="deployed-service-main__actions-img"
          src="/shared/static/folder-cloud.svg"
        />
        LOGS
      </RouterLink>

      <GoogleCryptospaceKeyDelete
        action
        :key-uuid="props.keyUuid"
        @finished="$router.replace(crumbs[crumbs.length - 2].to)"
      />
    </InformationAndActions>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, reactive, ref, watchEffect } from "vue";
import { useRoute } from "vue-router";

import { useBus } from "$shared/bus.js";

import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import GoogleCryptospaceKeyDelete from "@/components/google-cryptospace/GoogleCryptospaceKeyDelete.vue";
import GoogleCryptospaceKeyEdit from "@/components/google-cryptospace/GoogleCryptospaceKeyEdit.vue";
import UriTableRow from "@/components/google-cryptospace/UriTableRow.vue";
import InformationAndActions from "@/components/InformationAndActions.vue";
import { timestampToDate } from "@/misc.js";

const route = useRoute();

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
  keyUuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  key: {},
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "cryptospaceKey",
        params: route.params,
      },
      name: state.key?.objInfo?.name ?? "Key",
    },
  ];
});

function fetchResults() {
  axios
    .get(`/gekms/v1/keys/${props.keyUuid}`, {
      errorContext: "Failed to fetch key",
      loading,
    })
    .then((response) => {
      state.key = response.data;
    });
}

watchEffect(fetchResults);
useBus("updateCryptospaceKey", fetchResults);
</script>
