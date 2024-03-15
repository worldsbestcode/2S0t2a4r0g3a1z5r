<template>
  <div fluid class="fx-injection-controls">
    <div class="button-container">
      <fx-button
        class="mr-6"
        icon="mdi-check-circle-outline"
        text="START LOADING"
        :disabled="isInjecting"
        @click="injectSelectedDevices"
      />
      <fx-button
        class="mr-6"
        icon="mdi-close-circle-outline"
        text="STOP LOADING"
        theme="primary"
        :disabled="!isInjecting"
        @click="abortAllInjections"
      />
      <fx-button
        icon="mdi-cog-outline"
        text="SETTINGS"
        :disabled="isInjecting"
        @click="toggleSettingsDialog"
      />
    </div>
    <div class="info-container mt-3">
      <fx-check-box
        v-model:checked="selectAll"
        class="ml-3 mr-6"
        text="Select All"
        theme="primary"
      />

      <fx-count
        class="mr-3"
        title="Selected Terminals"
        :count="selectedDevicesCount"
      ></fx-count>
      <fx-count title="Total Terminals" :count="totalDevicesCount"></fx-count>
    </div>
    <fx-separator />
    <v-dialog v-model="showSerialDialog" max-width="720px" :persistent="true">
      <fx-update-serial
        v-model:serialNumber="serialNumber"
        @abort="cancel"
        @inject="inject(false)"
      />
    </v-dialog>
    <v-dialog v-model="showSettingsDialog" max-width="700px" :persistent="true">
      <fx-settings @close="toggleSettingsDialog" />
    </v-dialog>
  </div>
</template>

<script setup>
import { eInjectionStatus } from "@/utils/common";
import BigInt from "big-integer";
import { ref, watch, computed } from "vue";
import FxCount from "@/components/FXCount.vue";
import FxUpdateSerial from "@/components/FXUpdateSerial.vue";
import FxSettings from "@/components/FXSettings.vue";
import store from "@/store";

// variables
const selectAll = ref(false);
const indeterminate = ref(false);
const injectionList = ref([]);
const currentInjectingDevice = ref(null);
const serialNumber = ref(null);
const showSerialDialog = ref(false);
const showSettingsDialog = ref(false);
let interval = ref(null);

const isInjecting = computed(() => {
  return (
    currentInjectingDevice.value !== null || injectionList.value.length > 0
  );
});

// computed and watchers
const injectionStatusMap = computed(
  () => store.getters["pedinject/getInjectionStatusMap"],
);
const devices = computed(() => {
  return store.getters["pedinject/getDevices"];
});

const selectedDevicesCount = computed(() => {
  return devices.value.filter((device) => device.selected).length;
});

const totalDevicesCount = computed(() => {
  return devices.value.length;
});

/**
 * Injects the selected devices in order
 * watch for current injection for finsish or fail
 * before injecting the next device
 */
watch(injectionStatusMap, (updatedStatusMap) => {
  if (
    injectionList.value.length === 0 &&
    currentInjectingDevice.value === null
  ) {
    return;
  }

  if (currentInjectingDevice.value === null) {
    injectNextDevice();
  } else {
    let injectionResult = updatedStatusMap[currentInjectingDevice.value.id];

    if (injectionResult) {
      switch (injectionResult.status) {
        case eInjectionStatus.Finished:
          injectNextDevice();
          break;
        case eInjectionStatus.Failed:
          abortAllInjections();
          break;
        default:
          break;
      }
    }
  }
});

/*
 * If the user deselected a device after selecting all the devices
 * then the select all checkbox should be indeterminate
 */
watch(
  devices,
  (updatedDevices) => {
    if (selectAll.value) {
      let selected = updatedDevices.filter((device) => device.selected);
      indeterminate.value =
        selected.length > 0 && selected.length < updatedDevices.length;
    }
  },
  { deep: true },
);

/*
 * If the user toggle the select all checkbox, update all the devices
 */
watch(selectAll, (value) => {
  if (indeterminate.value) {
    indeterminate.value = false;
  }

  devices.value.forEach((device) => {
    device.selected = value;
  });

  store.dispatch("pedinject/updateDevices", { devices: devices.value });
});

// function
const getSerialNumber = async () => {
  let serviceId = store.getters["pedinject/getServiceId"];
  const params = {
    session: String(store.getters["pedinject/getSessionId"]),
    slot_id: BigInt(currentInjectingDevice.value.id),
    service_uuid: serviceId,
  };

  let serial_info = await store.dispatch("pedinject/getSerialNumber", params);
  return serial_info;
};

const cancel = async () => {
  showSerialDialog.value = false;
  inject(true);
};

/*
 * query the device serial number if supported before injecting
 */
const prepInjection = async () => {
  let serialInfo = await getSerialNumber();
  serialNumber.value = serialInfo.serialNumber;
  showSerialDialog.value = serialInfo.displaySerialPrompt;

  if (showSerialDialog.value) {
    showSerialDialog.value = true;
  } else if (serialInfo.error) {
    queryInjection();
    injectNextDevice();
  } else {
    inject(false);
  }
};

/*
 * inject the next device in the selected list
 */
const injectNextDevice = async () => {
  if (injectionList.value.length === 0) {
    currentInjectingDevice.value = null;
    clearQueryInterval();
    return;
  }

  let nextDevice = injectionList.value.shift();
  currentInjectingDevice.value = nextDevice;
  prepInjection();
};

/*
 * inject the current device
 */
const inject = async (serialNumEntryCancelled) => {
  showSerialDialog.value = false;
  let serviceId = store.getters["pedinject/getServiceId"];
  let params = {
    session: String(store.getters["pedinject/getSessionId"]),
    slot_id: BigInt(currentInjectingDevice.value.id),
    serial_num_entry_cancelled: serialNumEntryCancelled,
    service_uuid: serviceId,
  };

  if (serialNumber.value) {
    params.serial_number = String(serialNumber.value);
  }
  store.dispatch("pedinject/injectTerminal", params);
};

const abortAllInjections = async () => {
  injectionList.value = [];
  currentInjectingDevice.value = null;
};

const toggleSettingsDialog = () => {
  showSettingsDialog.value = !showSettingsDialog.value;
};

const injectSelectedDevices = async () => {
  startQueryInterval();
  let selectedDevices = devices.value.filter((device) => device.selected);
  injectionList.value = selectedDevices;
  injectNextDevice();
};

function startQueryInterval() {
  interval = ref(null);
  interval.value = setInterval(async () => {
    queryInjection();
  }, 300);
}

function queryInjection() {
  if (currentInjectingDevice.value) {
    let params = {
      slot_id: BigInt(currentInjectingDevice.value.id).value,
      session: String(store.getters["pedinject/getSessionId"]),
    };

    store.dispatch("pedinject/queryInjection", params);
  }
}

function clearQueryInterval() {
  if (interval.value) {
    clearInterval(interval.value);
    interval = ref(null);
  }
}
</script>

<style scoped>
.fx-injection-controls {
  display: block;
}
.button-container {
  display: flex;
}

.info-container {
  display: flex;
  width: 54%;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 0rem;
  width: fit-content;
}

.v-overlay {
  background-color: rgba(0, 0, 0, 0.7) !important;
  backdrop-filter: blur(5px) !important;
}
</style>
