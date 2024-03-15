<template>
  <div
    class="cover-screen"
    style="background: var(--secondary-background-color)"
  >
    <DeployedServiceHeader :crumbs="crumbs" />

    <StubsTable
      v-model:page="state.page"
      v-model:pageSize="state.pageSize"
      v-model:totalPages="state.totalPages"
      :data="state.keys"
      :export-name="`${state?.log?.objInfo?.name}-logs`"
      :search-keys="['Slot', 'Cryptogram']"
      empty-message="No keys found"
      title="Injection Log"
      :headers="['Slot', 'Key Type', 'KCV', 'Keyblock']"
    >
      <template #tableRows="{ data }">
        <tr v-for="(key, index) in data" :key="index">
          <td>
            {{ key.slot }}
          </td>
          <td>{{ key.keyType }}</td>
          <td>{{ key.checksum }}</td>
          <td>
            <div class="keyblock">
              {{ key.cryptogram }}
            </div>
          </td>
        </tr>
      </template>
    </StubsTable>
  </div>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, onBeforeMount, reactive } from "vue";
import { useRoute } from "vue-router";

import DeployedServiceHeader from "@/components/deploy-service/DeployedServiceHeader.vue";
import StubsTable from "@/components/StubsTable.vue";

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
  logUuid: {
    type: String,
    required: true,
  },
});

const state = reactive({
  keys: [],
  log: {},
  page: 0,
  totalPages: 1,
  pageSize: 15,
  keyExchangeHost: "",
  keyExchangeHosts: [],
  hostNames: [],
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: { name: "injectionLog", params: route.params },
      name: "Injection Log",
    },
  ];
});

onBeforeMount(() => {
  axios
    .get(`/dki/v1/logs/${props.logUuid}`, {
      errorContext: "Failed to fetch injection log",
    })
    .then((response) => {
      state.keys = response.data.injectedKeys;
      state.log = response.data;
    });

  axios.get("/dki/v1/hosts/").then((response) => {
    state.keyExchangeHosts = response.data.hosts;
    state.keyExchangeHosts.forEach((host) => {
      state.hostNames.push(host.name);
    });
  });
});
</script>

<style scoped>
.keyblock {
  max-width: 700px;
  overflow-wrap: anywhere;
}
</style>
