<template>
  <v-card>
    <v-card-title class="fx-card-title">
      <fx-label
        variant="plain"
        text="Service Settings"
        color="var(--primary-color)"
      />
      <fx-button variant="plain" icon="mdi-close" @click="emit('close')" />
    </v-card-title>
    <fx-separator />
    <v-card-text>
      <fx-label
        class="mb-5"
        text="Update terminal serial communctaion settings."
      />
      <fx-combobox
        v-model:input="baudRate"
        :options="baudRateOptions"
        text="Baud Rate: "
      />

      <fx-combobox
        v-model:input="dataBits"
        class="ml-2 my-2"
        :options="dataBitsOptions"
        text="Data Bits: "
      />

      <fx-combobox
        v-model:input="stopBits"
        class="ml-2 my-2"
        :options="stopBitsOptions"
        text="Stop Bits: "
      />

      <fx-combobox
        v-model:input="parity"
        class="ml-8"
        :options="parityOptions"
        text="Parity:"
      />
    </v-card-text>
    <v-card-actions>
      <div class="fx-serial-button-container">
        <fx-button
          theme="primary"
          text="CLOSE"
          icon="mdi-close"
          @click="emit('close')"
        />
        <fx-button
          text="SAVE"
          icon="mdi-content-save-cog-outline"
          theme="primary"
          variant="tonal"
          @click="updateSettings"
        />
      </div>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { defineEmits, ref, onBeforeMount } from "vue";
import { updateSerialSettings, getSerialSettings } from "@/utils/common.js";
import store from "@/store";
const baudRateOptions = [
  "1200",
  "2400",
  "4800",
  "9600",
  "19200",
  "38400",
  "57600",
  "115200",
  "230400",
  "460800",
];
const baudRate = ref("1200");
const dataBits = ref("5");
const parity = ref("None");
const stopBits = ref("1");

const dataBitsOptions = ["5", "6", "7", "8"];
const parityOptions = ["None", "Even", "Odd"];
const stopBitsOptions = ["1", "2"];
const emit = defineEmits(["close"]);

const updateSettings = () => {
  let parityBit = "ParityInvalid";
  switch (parity.value) {
    case "None":
      parityBit = "ParityNone";
      break;
    case "Odd":
      parityBit = "ParityOdd";
      break;
    case "Even":
      parityBit = "ParityEven";
      break;
    default:
      break;
  }

  let settings = {
    baud: Number(baudRate.value),
    dataBits: Number(dataBits.value),
    parity: parityBit,
    stopBits: Number(stopBits.value),
  };

  const deviceGroupUuid = store.getters["serviceInfo/getDeviceGroupUuid"];
  const sessionUuid = store.getters["pedinject/getSessionId"];

  const requestSettings = {
    sessionUuid: sessionUuid,
    serialSettings: settings,
  };
  updateSerialSettings(deviceGroupUuid, requestSettings);
  emit("close");
};

onBeforeMount(() => {
  const deviceGroupUuid = store.getters["serviceInfo/getDeviceGroupUuid"];
  getSerialSettings(deviceGroupUuid).then((serialSettings) => {
    baudRate.value = String(serialSettings.baud);
    dataBits.value = String(serialSettings.dataBits);
    parity.value = serialSettings.parity;
    stopBits.value = String(serialSettings.stopBits);
    let parityBit = "";

    switch (serialSettings.parity) {
      case "ParityNone":
        parityBit = "None";
        break;
      case "ParityEven":
        parityBit = "Even";
        break;
      case "ParityOdd":
      default:
        parityBit = "Odd";
        break;
    }

    parity.value = parityBit;
  });
});
</script>

<style scoped>
.fx-card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fx-serial-button-container {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2.5rem;
}
</style>
