<template>
  <div
    class="cover-screen"
    style="background: var(--secondary-background-color)"
  >
    <DeployedServiceHeader :crumbs="crumbs" />

    <StubsTable
      v-model:page="pagination.page"
      v-model:pageSize="pagination.pageSize"
      v-model:totalPages="pagination.totalPages"
      :data="pagination.results"
      :description="`This page shows all the device loading events. Each device loading event represents an instance in which one or more keys were injected.`"
      empty-message="No injection logs found"
      :export-name="`${serviceData?.objInfo?.name}-logs`"
      :headers="[
        'Date',
        'Serial Number',
        '# of injected keys',
        'status',
        'actions',
      ]"
      :loading="loading"
      :search-keys="['Date', 'Serial Number', '# of injected keys', 'status']"
      title="Device Loading Events"
    >
      <template #exportButton>
        <Modal title="Export Keys Under Key Exchange Host">
          <template #button="{ on }">
            <button class="button-no-styling" v-on.stop="on">
              <img src="/shared/static/export-to-csv.svg" />Export Injection
              Report
            </button>
          </template>
          <template #content="{ toggleModal }">
            <GenericSelector
              v-model:selectedObject="state.keyExchangeHost"
              title="Key Exchange Host"
              hint="keys will be exported under the major key if no host is selected"
              empty-text="No host selected"
              :objects="state.hostNames"
              :display="
                (host) => {
                  return host.name;
                }
              "
            />
            <div class="modal-button-bottom">
              <button class="button-secondary" @click="toggleModal">
                CANCEL
              </button>
              <button
                class="button-primary"
                @click="
                  () => {
                    startExportProcess();
                    toggleModal();
                  }
                "
              >
                EXPORT KEYS
              </button>
            </div>
          </template>
        </Modal>
      </template>
      <template #tableRows="{ data }">
        <tr
          v-for="logItem in data"
          :key="logItem.oid"
          v-on.stop="on"
          @click="viewInjectionLog(logItem)"
        >
          <td>{{ unixDateToString(logItem.objInfo.creationDate) }}</td>
          <td>{{ logItem.serial }}</td>
          <td>{{ logItem.injectedKeys.length }}</td>
          <td>{{ logItem.successful ? "success" : "failed" }}</td>
          <td>
            <div class="button-icon-row">
              <ChcTooltipButtonIcon
                class="table__link"
                icon="key"
                tooltip="View Keys"
                @click="viewKeys(logItem)"
              />
              <ChcTooltipButtonIcon
                class="table__link"
                icon="lab_profile"
                tooltip="View Device Logs"
                @click="viewLog(logItem)"
              />
            </div>
          </td>
        </tr>
      </template>
    </StubsTable>
  </div>
  <RouterView :crumbs="crumbs" :service-uuid="props.serviceUuid" />
</template>

<script setup>
import axios from "axios";
import {
  computed,
  defineProps,
  inject,
  onMounted,
  reactive,
  ref,
  watchEffect,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";

import ChcTooltipButtonIcon from "$shared/components/ChcTooltipButtonIcon.vue";
import Modal from "$shared/components/Modal.vue";

import DeployedServiceHeader from "@/components/deploy-service/DeployedServiceHeader.vue";
import GenericSelector from "@/components/dki/GenericSelector.vue";
import StubsTable from "@/components/StubsTable.vue";
import { stubsSynchronize } from "@/misc.js";

const route = useRoute();
const router = useRouter();
const toast = useToast();

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
  sessionUuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);
const log = ref(null);
const pagination = reactive({
  page: 1,
  pageSize: 15,
  totalPages: 1,
  results: [],
});

const state = reactive({
  keyExchangeHost: "",
  keyExchangeHosts: [],
  hostNames: [],
  logs: [],
  report: "",
  host: undefined,
  log: undefined,
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: { name: "deviceLoadingEvents", params: route.params },
      name: "Device Loading Events",
    },
  ];
});

const unixDateToString = (unixDate) => {
  const date = new Date(unixDate * 1000);
  return date.toLocaleString();
};

const viewInjectionLog = (selectedLog) => {
  log.value = selectedLog;
};

function fetchResults() {
  axios
    .get(`/dki/v1/logs/query`, {
      params: {
        page: pagination.page,
        pageSize: pagination.pageSize,
        serviceUuid: props.serviceUuid,
        sessionUuid: route.params.sessionUuid,
      },
      errorContext: "Failed to fetch logs",
      loading,
    })
    .then((response) => {
      stubsSynchronize(response, pagination, "results");
    });
}

function getAllLogs() {
  axios
    .get(`/dki/v1/logs/query`, {
      params: {
        page: 1,
        pageSize: 10000, // 10,000 is the max
        serviceUuid: props.serviceUuid,
        sessionUuid: route.params.sessionUuid,
      },
      errorContext: "Failed to fetch logs",
      loading,
    })
    .then((response) => {
      state.logs = response.data.results;

      exportKeys();
    });
}

function viewLog(log) {
  router.push({
    name: "injectionLog",
    params: {
      logUuid: log.objInfo.uuid,
    },
  });
}

function viewKeys(log) {
  router.push({
    name: "injectedKeys",
    params: {
      logUuid: log.objInfo.uuid,
    },
  });
}

function startExportProcess() {
  initializeReport();
  let queryLogs = true;
  if (state.keyExchangeHost) {
    let host = state.keyExchangeHosts.find((host) => {
      return host.name === state.keyExchangeHost;
    });

    if (host) {
      state.host = host;
    } else {
      toast.error("Invaild host selected");
      state.keyExchangeHost = "";
      queryLogs = false;
    }
  }

  if (queryLogs) {
    getAllLogs();
  }
}

function download(file, fileName) {
  if (typeof file === "string") {
    file = file.split("");
  }

  let a = document.createElement("a");
  let blob = new Blob(file);
  let blobUrl = window.URL.createObjectURL(blob);
  a.href = blobUrl;
  a.download = fileName;
  a.click();
  window.URL.revokeObjectURL(blobUrl);
}

function getLogMessageForKey(keyType, slot) {
  let logMessage = state.log.logMessages.find((logMessage) => {
    let msg = logMessage.msg;
    return msg.includes(keyType) && msg.includes(slot);
  });

  return logMessage;
}

function initializeReport() {
  state.report = "Key Injection Report for keys exported under ";
  if (state.keyExchangeHost) {
    state.report +=
      "the KTK associated with host " + state.keyExchangeHost.name + "\n";
  } else {
    state.report += "the major key\n";
  }

  state.report +=
    "Injection Date and Time, Key Type, Device Serial Number, Key Location, Key Block/Cryptogram, Checksum, KSN, Pass/Fail , Log Summary\n";
}

function generateLogReport(keys) {
  keys.forEach((key) => {
    let logMessage = getLogMessageForKey(key.keyType, key.slot);
    let timeStamp = logMessage
      ? logMessage.timeStamp
      : state.log.logMessage[0].timeStamp;
    let summary = logMessage ? logMessage.msg : "";
    let status = state.log.successful ? "PASS" : "FAIL";
    let ksn = key.ksn ? key.ksn : "";
    state.report +=
      timeStamp +
      "," +
      key.keyType +
      "," +
      state.log.serial +
      "," +
      key.slot +
      "," +
      key.cryptogram +
      "," +
      key.checksum +
      "," +
      ksn +
      "," +
      status +
      "," +
      summary +
      "\n";
  });
}

function exportKeys() {
  state.log = state.logs.shift();
  if (state.log) {
    if (state.host) {
      axios
        .post("/dki/v1/hosts/translate", {
          host: state.host,
          keys: state.log.injectedKeys,
        })
        .then((response) => {
          generateLogReport(response.data.keys);
          exportKeys();
        });
    } else {
      generateLogReport(state.log.injectedKeys);
      exportKeys();
    }
  } else {
    download(state.report, "Key Injection Report.csv");
  }
}

onMounted(() => {
  fetchResults();

  axios.get("/dki/v1/hosts/").then((response) => {
    state.keyExchangeHosts = response.data.hosts;
    state.keyExchangeHosts.forEach((host) => {
      state.hostNames.push(host.name);
    });
  });
});

watchEffect(() => {
  if (route.params.sessionUuid) {
    fetchResults();
  }
});
</script>

<style scoped>
.button-icon-row {
  display: flex;
}

.deployed-manage-table .table__link {
  border: 0;
  padding: 0;
  background: 0;
  font-weight: initial;
  color: var(--primary-text-color);
}

.deployed-manage-table tbody tr:hover .table__link {
  color: var(--primary-color);
  text-decoration: underline;
}

.modal-button-bottom {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  justify-content: space-between;
}
</style>
