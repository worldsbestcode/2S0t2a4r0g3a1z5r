<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <StubsTable
      v-model:page="state.page"
      v-model:pageSize="state.pageSize"
      v-model:totalPages="state.totalPages"
      :data="state.results"
      :description="`Account activity is tracked in audit-friendly logs. Logs allow you to view data including how many times a key is used, which application or project it was used for, which users interacted with it, and what actions were taken. Logs can be exported in CSV format.`"
      empty-message="No logs found"
      :export-name="`${serviceData?.objInfo?.name}-logs`"
      :headers="['Type', 'Summary', 'Time', 'Users']"
      :loading="loading"
      :search-keys="['logType', 'summary']"
      title="Logs"
    >
      <template #tableRows="{ data }">
        <tr v-for="log in data" :key="log.summary">
          <td>{{ log.logType }}</td>
          <td>{{ log.summary }}</td>
          <td>{{ log.time }}</td>
          <td>{{ log.users.join(", ") }}</td>
        </tr>
      </template>
      <template #batchExportButton>
        <Modal title="Export Logs">
          <template #button="{ on }">
            <button class="button-no-styling" v-on.stop="on">
              <img src="/shared/static/export-to-csv.svg" />Export Filtered
            </button>
          </template>
          <template #content="{ toggleModal }">
            <ChcInput
              v-model="state.startDate"
              label="Start Date"
              type="datetime-local"
            />
            <ChcInput
              v-model="state.endDate"
              label="End Date"
              type="datetime-local"
            />
            <ChcSelect
              v-model="state.currentExportFormat"
              label="Export Format"
            >
              <option
                v-for="format of exportFormats"
                :key="format"
                :value="format"
              >
                {{ format }}
              </option>
            </ChcSelect>
            <ModalFooter
              :text="'EXPORT'"
              @action="exportToCsv"
              @cancel="toggleModal"
            />
          </template>
        </Modal>
      </template>
    </StubsTable>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, inject, reactive, ref, watchEffect } from "vue";
import { useRoute } from "vue-router";

import ChcInput from "$shared/components/ChcInput.vue";
import ChcSelect from "$shared/components/ChcSelect.vue";
import Modal from "$shared/components/Modal.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

import { downloadEndpointFile } from "@/components/client-app/client-app.js";
import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import StubsTable from "@/components/StubsTable.vue";
import { stubsSynchronize } from "@/misc.js";

const route = useRoute();

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
  cryptospaceUuid: {
    type: String,
    default: undefined,
  },
  keyUuid: {
    type: String,
    default: undefined,
  },
  userUuid: {
    type: String,
    default: undefined,
  },
});

const loading = ref(false);

const exportFormats = ["JSON", "CSV"];

const state = reactive({
  page: 1,
  pageSize: 15,
  totalPages: 1,
  results: [],
  startDate: "1970-01-01T00:00",
  endDate: "9999-12-31T23:59",
  currentExportFormat: exportFormats[0],
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "deployedServiceLogs",
        params: route.params,
      },
      name: "Logs",
    },
  ];
});

function attributeQuery() {
  if (props.keyUuid) {
    return `gekms_key=${props.keyUuid}`;
  }

  if (props.cryptospaceUuid) {
    return `cryptospace=${props.cryptospaceUuid}`;
  }

  if (props.userUuid) {
    return `user=${props.userUuid}`;
  }
}

function fetchResults() {
  axios
    .get(`/cuserv/v1/auditlogs/${props.serviceUuid}`, {
      params: {
        page: state.page,
        pageSize: state.pageSize,
        attribute_query: attributeQuery(),
      },
      errorContext: "Failed to fetch logs",
      loading,
    })
    .then((response) => {
      stubsSynchronize(response, state, "logs");
    });
}
watchEffect(fetchResults);

function exportToCsv() {
  axios
    .get(`/cuserv/v1/auditlogs/${props.serviceUuid}/export`, {
      params: {
        attribute_query: attributeQuery(),
        start_date: state.startDate.replace("T", " ") + ":00",
        end_date: state.endDate.replace("T", " ") + ":00",
        export_format: state.currentExportFormat,
      },
      errorContext: "Failed to export logs",
      loading,
    })
    .then((response) => {
      downloadEndpointFile(
        response.data["result"],
        "logs",
        serviceData.value.objInfo.name,
      );
    });
}
</script>
