<template>
  <DeployedServiceWrapper :crumbs="crumbs" :loading="loading">
    <InformationAndActions
      :title="state.key?.name ?? 'Key'"
      description=""
      :table-items="[
        ['Name', state.key?.name],
        ['Start Validity', state.key?.startValidity],
        ['Expiration', state.key?.endValidity],
        ['Checksum', state.key?.checksum],
        ['User email', state.email],
        ['Service name', state.serviceName],
      ]"
    >
      <template #actions>
        <GooglePersonalKeyDelete
          icon
          :service-uuid="props.serviceUuid"
          :email="props.email"
          :key-uuid="props.keyUuid"
          @finished="$router.replace(crumbs[crumbs.length - 2].to)"
        />
      </template>

      <GooglePersonalKeyDelete
        action
        :service-uuid="props.serviceUuid"
        :email="props.email"
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
import GooglePersonalKeyDelete from "@/components/google-user/GooglePersonalKeyDelete.vue";
import InformationAndActions from "@/components/InformationAndActions.vue";

const route = useRoute();

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
  keyUuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  key: {},
  email: "",
  serviceName: "",
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "personalKey",
        params: route.params,
      },
      name: state.key?.name ?? "Key",
    },
  ];
});

function fetchResults() {
  axios
    .get(`/gcse/v1/keys/${props.keyUuid}`, {
      errorContext: "Failed to fetch key",
      loading,
    })
    .then((response) => {
      state.key = response.data.key;
      state.email = response.data.email;
      state.serviceName = response.data.serviceName;
    });
}

watchEffect(fetchResults);
useBus("updatePersonalKey", fetchResults);
</script>
