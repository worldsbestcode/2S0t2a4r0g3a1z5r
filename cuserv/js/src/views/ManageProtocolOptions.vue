<template>
  <div
    class="cover-screen"
    style="background: var(--secondary-background-color)"
  >
    <DeployedServiceHeader :crumbs="crumbs"></DeployedServiceHeader>
    <div class="protocol-options__main">
      <div class="protocol-options__title">Protocol Options</div>
      <div class="protocol-options__description">
        Manage the options for the {{ protocolName }} protocol.
      </div>
      <ChcToggle
        v-model:modelValue="state.printerEnabled"
        small
        side="right"
        label="Enable Label Printer"
      ></ChcToggle>
      <component
        :is="state.component"
        v-model:options="state.options"
        :protocol="state.protocol"
      ></component>
      <div class="dki-footer">
        <button class="button-primary" @click="updateProtocolOptions">
          UPDATE
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import StatusCodes from "http-status-codes";
import { computed, defineProps, onBeforeMount, reactive } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

import ChcToggle from "$shared/components/ChcToggle.vue";
import { eProtocols, getProtocolName } from "$shared/utils/protocol";

import DeployedServiceHeader from "@/components/deploy-service/DeployedServiceHeader.vue";
import FuturexProtocolOptions from "@/components/dki/protocol-options/FuturexProtocolOptions.vue";
import FXSPProtocolOptions from "@/components/dki/protocol-options/FXSPProtocolOptions.vue";
import IngenicoNarProtocolOptions from "@/components/dki/protocol-options/IngenicoNarProtocolOptions.vue";
import KitBridgeProtocolOptions from "@/components/dki/protocol-options/KitBridgeProtocolOptions.vue";
import VeriFoneProtocolOptions from "@/components/dki/protocol-options/VeriFoneProtocolOptions.vue";

const toast = useToast();
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

const state = reactive({
  component: null,
  options: null,
  protocol: eProtocols.eProtocolNone,
  deviceGroupUuid: "",
  printerEnabled: false,
});

const route = useRoute();

const protocolName = computed(() => {
  return getProtocolName(state.protocol);
});
const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: { name: "manageProtocolOptions", params: route.params },
      name: "Protocol Options",
    },
  ];
});

function protocolOptionsComponent(protocol) {
  let component = null;
  switch (protocol) {
    case eProtocols.eIngenicoKiTBridge:
      component = KitBridgeProtocolOptions;
      break;
    case eProtocols.eVeriFonePP1000SE:
    case eProtocols.eVeriFoneIPP8:
      component = VeriFoneProtocolOptions;
      break;
    case eProtocols.eIngenicoNar:
      component = IngenicoNarProtocolOptions;
      break;
    case eProtocols.eFuturex:
      component = FuturexProtocolOptions;
      break;
    case eProtocols.eFXSP:
      component = FXSPProtocolOptions;
      break;
    default:
      break;
  }

  return component;
}

function updateProtocolOptions() {
  axios
    .patch(`/dki/v1/device/${state.deviceGroupUuid}`, {
      options: state.options,
      printerEnabled: state.printerEnabled,
    })
    .then((response) => {
      if (response.status === 200) {
        toast("Successfully updated protocol options");
      }
    });
}

function getDeviceGroupInfo(deviceUuid) {
  state.deviceGroupUuid = deviceUuid;
  axios
    .get(`/dki/v1/device/${deviceUuid}`, {
      errorContext: "Failed to fetch device group info",
    })
    .then((response) => {
      if (response.status === StatusCodes.OK) {
        let deviceGroupInfo = response.data;
        state.protocol = deviceGroupInfo.protocolId;
        state.options = deviceGroupInfo.options;
        state.printerEnabled = deviceGroupInfo.printerEnabled;
        state.component = protocolOptionsComponent(state.protocol);
      }
    });
}

function getServiceInfo() {
  axios
    .get(`/cuserv/v1/services/${props.serviceUuid}`, {
      errorContext: "Failed to fetch PED inject services",
    })
    .then((response) => {
      if (response.status === StatusCodes.OK) {
        response.data.associatedObjects.forEach((associatedObject) => {
          if (associatedObject.purpose === "DeviceGroup") {
            getDeviceGroupInfo(associatedObject.associatedUuid);
          }
        });
      }
    });
}

onBeforeMount(() => {
  getServiceInfo();
});
</script>

<style scoped>
.protocol-options__main {
  max-width: 80rem;
  margin: auto;
}

.protocol-options__title {
  font-weight: 700;
  font-size: 28px;
}

.protocol-options__description {
  color: var(--secondary-text-color);
  margin-bottom: 3.5rem;
  white-space: pre-line;
}

.dki-footer {
  width: fit-content;
  margin-left: auto;
  margin-right: 0rem;
  padding: 1.5rem 0rem;
}
</style>
