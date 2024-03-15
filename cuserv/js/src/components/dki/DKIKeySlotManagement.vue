<template>
  <div
    class="cover-screen"
    style="background: var(--secondary-background-color)"
  >
    <DeployedServiceHeader :crumbs="crumbs"></DeployedServiceHeader>
    <StubsTable
      :data="state.keySlots"
      title="Manage Key Slots"
      description="Manage the key slots associated to this service."
      empyt-message="No key slots found"
      :search-keys="['objInfo.name']"
      :headers="['Slot', 'Key Name', 'Required', 'Actions']"
      :loading="false"
      hide-pagination
    >
      <template #exportButton>
        <Modal title="Download Key Slot and Serivce Barcodes">
          <template #button="{ on }">
            <button class="button-no-styling" v-on.stop="on">
              <img src="/shared/static/printer-active.svg" /> Download Barcodes
            </button>
          </template>
          <template #content="{ toggleModal }">
            <DownloadBarcodes
              :barcodes="state.barcodes"
              @downloaded="toggleModal"
              @cancel="toggleModal"
            ></DownloadBarcodes>
          </template>
        </Modal>
      </template>
      <template #addButton>
        <DKIKeySlotEdit
          :service-uuid="props.serviceUuid"
          :protocol="state.protocol"
          :restricted-keys="state.restrictedKeys"
          :key-slot-info="state.keySlotInfo"
          v-bind="$attrs"
          @finished="getServiceInfo"
        ></DKIKeySlotEdit>
      </template>
      <template #tableRows="{ data }">
        <tr
          v-for="keySlot in data"
          :key="keySlot.objInfo.uuid"
          style="cursor: pointer"
          @click="toggleEditModal($event, keySlot)"
        >
          <td>{{ keySlot.slot }}</td>
          <td>{{ keySlot.objInfo.name }}</td>
          <td>{{ keySlot.required ? "YES" : "NO" }}</td>
          <td>
            <DKIKeySlotDelete
              :key-slot-uuid="keySlot.objInfo.uuid"
              text
              @refreshContent="getServiceInfo"
            ></DKIKeySlotDelete>
          </td>
        </tr>
      </template>
    </StubsTable>
    <Modal title="Edit Key Slot">
      <template #button="{ on }">
        <div ref="editModal" v-on.stop="on"></div>
      </template>
      <template #content="{ toggleModal }">
        <DKIKeySlotEditBody
          :service-uuid="props.serviceUuid"
          :key-slot-uuid="state.currentKeySlot.objInfo.uuid"
          :protocol="state.protocol"
          :restricted-keys="state.restrictedKeys"
          :key-slot-info="state.keySlotInfo"
          edit
          @cancel="toggleModal"
          @finished="handleFinished(toggleModal)"
        ></DKIKeySlotEditBody>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import axios from "axios";
import StatusCodes from "http-status-codes";
import { computed, defineProps, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";

import Modal from "$shared/components/Modal.vue";
import { encodeUuidToBarcode } from "$shared/utils/barcode.js";
import { KeyRestrictionSet } from "$shared/utils/keys.js";
import { eProtocols } from "$shared/utils/protocol.js";

import DeployedServiceHeader from "@/components/deploy-service/DeployedServiceHeader.vue";
import DKIKeySlotDelete from "@/components/dki/DKIKeySlotDelete.vue";
import DKIKeySlotEdit from "@/components/dki/DKIKeySlotEdit.vue";
import DKIKeySlotEditBody from "@/components/dki/DKIKeySlotEditBody.vue";
import DownloadBarcodes from "@/components/dki/DownloadBarcodes.vue";
import StubsTable from "@/components/StubsTable.vue";

const route = useRoute();

const props = defineProps({
  serviceName: {
    type: String,
    required: true,
  },
  crumbs: {
    type: Array,
    required: true,
  },
  serviceUuid: {
    type: String,
    required: true,
  },
});

const editModal = ref(null);

const state = reactive({
  keySlots: [],
  currentKeySlot: null,
  protocol: eProtocols.eProtocolNone,
  restrictedKeys: new KeyRestrictionSet(),
  keySlotInfo: {},
  barcodes: [],
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: { name: "manageKeySlots", params: route.params },
      name: "Manage Key Slots",
    },
  ];
});

function getDeviceGroupInfo(deviceUuid) {
  axios
    .get(`/dki/v1/device/${deviceUuid}`, {
      errorContext: "Failed to fetch device group info",
    })
    .then((response) => {
      if (response.status === StatusCodes.OK) {
        let deviceGroupInfo = response.data;
        try {
          state.keySlotInfo = JSON.parse(
            deviceGroupInfo.protocolJsonData,
          ).keySlotInfo;
        } catch (error) {
          console.error("Failed to protocol data: " + error);
        }

        state.protocol = deviceGroupInfo.protocolId;

        state.restrictedKeys = new KeyRestrictionSet();
        deviceGroupInfo.restrictedKeys.forEach((keyRestriction) => {
          state.restrictedKeys.setComboArray(
            keyRestriction.keyType,
            keyRestriction.keyLengths,
          );
        });
      }
    });
}

function getServiceInfo() {
  state.barcodes = [];
  axios
    .get(`/cuserv/v1/services/${props.serviceUuid}`, {
      errorContext: "Failed to fetch PED inject services",
    })
    .then((response) => {
      if (response.status === StatusCodes.OK) {
        let keySlotRefIds = [];
        state.barcodes.push({
          title: "Service: " + response.data.objInfo.name,
          data: encodeUuidToBarcode(response.data.objInfo.uuid),
        });
        response.data.associatedObjects.forEach((associatedObject) => {
          if (associatedObject.purpose === "KeySlotReference") {
            keySlotRefIds.push(associatedObject.associatedUuid);
          } else if (associatedObject.purpose === "DeviceGroup") {
            getDeviceGroupInfo(associatedObject.associatedUuid);
          }
        });
        getKeySlotReferences(keySlotRefIds);
      }
    });
}

function getKeySlotReferences(keySlotRefIds) {
  axios
    .post(
      "/dki/v1/keyslots/refs",
      {
        uuids: keySlotRefIds,
      },
      {
        errorContext: "Failed to query key slot references",
      },
    )
    .then((response) => {
      let keySlots = response.data.results;
      state.keySlots = keySlots.sort((a, b) => a.slot - b.slot);

      state.keySlots.forEach((keySlot) => {
        state.barcodes.push({
          title: "Key Name: " + keySlot.objInfo.name,
          data: encodeUuidToBarcode(keySlot.objInfo.uuid),
        });
      });
    });
}

function handleFinished(toggleModal) {
  toggleModal();
  getServiceInfo();
}

function toggleEditModal(event, keySlot) {
  if (event.target.tagName === "BUTTON") {
    return;
  }
  state.currentKeySlot = keySlot;
  const clickEvent = new Event("click");
  editModal.value.dispatchEvent(clickEvent);
}

onMounted(getServiceInfo);
</script>

<style scoped>
.key-slot-table {
  width: 100%;
}

.key-slot-table thead,
.key-slot-table tbody {
  border-bottom: 1px solid;
}

.key-slot-table tr {
  height: 44px;
}

.key-slot-table th {
  font-weight: 700;
}

.key-slot-table tbody tr + tr {
  border-top: 1px solid var(--border-color);
}

.key-slot-table tbody tr td {
  color: var(--muted-text-color);
}

.key-slot-table tbody tr:hover {
  background: var(--secondary-background-color);
}

.key-slot-table tbody tr:hover td {
  color: var(--primary-text-color);
}
</style>
