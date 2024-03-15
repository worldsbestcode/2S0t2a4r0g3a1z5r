<template>
  <fx-expansion-panel :disable-expansion="!terminalPath">
    <template #fx-expansion-header>
      <fx-expansion-header>
        <fx-check-box
          v-model:checked="selected"
          class="ml-3 mr-5"
          :text="terminalName"
          theme="primary"
        />
        <terminal-status-info :terminal-id="props.terminalId" />
      </fx-expansion-header>
    </template>
    <template #fx-expansion-content>
      <fx-expansion-content>
        <fx-label class="ml-5 pb-3" :text="terminalPath" />
      </fx-expansion-content>
    </template>
  </fx-expansion-panel>
</template>

<script setup>
import { computed, defineProps } from "vue";
import store from "@/store";
import { eSlotTypes } from "@/utils/common";
import BigInt from "big-integer";

import TerminalStatusInfo from "@/components/TerminalStatusInfo.vue";

const props = defineProps({
  terminalId: {
    type: BigInt,
    required: true,
  },
  index: {
    type: Number,
    required: true,
  },
});

const selected = computed({
  get() {
    return store.getters["pedinject/getDevices"].find(
      (device) => device.id === props.terminalId,
    ).selected;
  },

  set(value) {
    let device = store.getters["pedinject/getDevices"].find(
      (device) => device.id === props.terminalId,
    );

    device.selected = value;
    store.dispatch("pedinject/updateDevice", { device: device });
  },
});

const serialPortsPerCard = 4;
const usbPortsPerHub = 6;

const getFirmwarePortName = (cardIndex, portIndex) => {
  let portName = "";
  if (portIndex <= serialPortsPerCard) {
    portName = "Card " + cardIndex + " - " + "Serial " + portIndex;
  } else {
    let usbPort = portIndex - serialPortsPerCard - 1;
    let usbHub = Math.floor(usbPort / usbPortsPerHub) + 1;

    // wrap the usb port numbers so the range from 1 - 6;
    let wrappedUsbPort = (usbPort % usbPortsPerHub) + 1;
    portName = "Usb Hub " + usbHub + " - Port " + wrappedUsbPort;
  }
  return portName;
};

const terminalName = computed(() => {
  let device = store.getters["pedinject/getDevices"].find(
    (device) => device.id === props.terminalId,
  );

  let name = "USB Device " + props.index;
  switch (device.type) {
    case eSlotTypes.Host:
      name = "Host USB " + props.index;
      break;
    case eSlotTypes.Firmware:
      name = getFirmwarePortName(device.cardIndex, device.slotIndex);
      break;
  }

  return name;
});

const terminalPath = computed(() => {
  var path = null;

  const terminal = store.getters["pedinject/getDevices"].find(
    (device) => device.id === props.terminalId,
  );

  if (terminal && terminal.extraInfo.length > 0) {
    let ttyPath = terminal.extraInfo[0];
    if (ttyPath.length > 0) {
      path = ttyPath;
    }
  }

  return path;
});
</script>
