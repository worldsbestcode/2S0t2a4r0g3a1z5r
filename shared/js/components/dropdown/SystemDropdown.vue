<template>
  <Dropdown right>
    <template #button="{ on }">
      <button class="icon-button" v-on="on">
        <img src="/shared/static/icons/info.svg" />
      </button>
    </template>

    <header>
      System Information
      <template v-if="state.info">- {{ state.info.hostname }}</template>
    </header>
    <LoadingSpinner v-if="state.loading" :loading="state.loading" />
    <template v-else-if="state.error">
      <div>Failed to load system information</div>
    </template>
    <template v-else-if="state.info">
      <table class="key-value">
        <tr v-for="key in infoKeysToDisplay" :key="key">
          <th>{{ infoKeysApiToHumanReadable[key] }}</th>
          <td>{{ state.info[key] }}</td>
        </tr>
      </table>
    </template>
  </Dropdown>
</template>

<script setup>
import { reactive } from "vue";

import axios from "$shared/axios.js";
import Dropdown from "$shared/components/Dropdown.vue";
import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

const infoKeysApiToHumanReadable = {
  hostname: "Hostname",
  hsmHash: "HSM hash",
  hsmModel: "HSM model",
  hsmSerial: "HSM serial",
  hsmVersion: "HSM version",
  product: "Product",
  serial: "Serial",
  systemHash: "System hash",
  version: "Version",
};

const infoKeysToDisplay = [
  "product",
  "serial",
  "systemHash",
  "version",
  "versionHash",
  "hsmModel",
  "hsmSerial",
  "hsmHash",
  "hsmVersion",
];

const state = reactive({
  loading: true,
  error: false,
  info: null,
  licenses: null,
});

axios
  .get("/home/v1/dashboard/info")
  .then((response) => {
    const info = response.data;
    state.licenses = info.licenses;
    for (const infoKey in info) {
      if (!Object.keys(infoKeysApiToHumanReadable).includes(infoKey)) {
        delete info[infoKey];
      }
    }

    state.info = info;
  })
  .catch(() => {
    state.error = true;
  })
  .finally(() => {
    state.loading = false;
  });
</script>

<style scoped>
.key-value th {
  text-align: right;
  padding-right: 12px;
  font-weight: 500;
}

.key-value th,
.key-value td {
  padding: 0;
  padding-right: 12px;
}
</style>
