<template>
  <TaskSkeleton
    title="Networking"
    :loading="loading"
    @finish="updateNetwork({ finish: true })"
  >
    <ChcToggle
      v-model="state.advancedMode"
      label="Advanced mode"
      hint="Allows bonding and routes"
    />

    <NetworkingDns v-model="state.dnsServers" />

    <NetworkingBonding
      v-if="state.advancedMode"
      v-model:networkPorts="state.networkPorts"
      v-model:activeNetworkPort="state.activeNetworkPort"
    />

    <template v-if="state.activeNetworkPort">
      <ChcSelect v-model="state.activeNetworkPort" label="Port">
        <option v-for="port in selectablePorts" :key="port.name" :value="port">
          {{ port.name }}
        </option>
      </ChcSelect>

      <NetworkingRoutes
        v-if="state.advancedMode"
        v-model="state.activeNetworkPort.routes"
      />

      <ChcSelect v-model="state.activeInterface" label="Interface">
        <template v-if="state.activeNetworkPort.interfaces.length > 0">
          <option
            v-for="networkInterface in state.activeNetworkPort.interfaces"
            :key="networkInterface.name"
            :value="networkInterface"
          >
            {{ networkInterface.name }}
          </option>
        </template>
        <option v-else :value="undefined">No interfaces found</option>
      </ChcSelect>

      <NetworkingInterfaces
        v-model="state.activeInterface"
        v-model:interfaces="state.activeNetworkPort.interfaces"
        :network-port-name="state.activeNetworkPort.name"
      />
    </template>

    <template #footer>
      <ChcButton secondary @click="initializeNetworkConfiguration">
        Refresh
      </ChcButton>
      <ChcButton secondary @click="updateNetwork({ finish: false })">
        Apply
      </ChcButton>
    </template>
  </TaskSkeleton>
</template>

<script setup>
import axios from "axios";
import { computed, reactive, ref, watch } from "vue";
import { useToast } from "vue-toastification";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcSelect from "$shared/components/ChcSelect.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";

import NetworkingBonding from "@/components/NetworkingBonding.vue";
import NetworkingDns from "@/components/NetworkingDns.vue";
import NetworkingInterfaces from "@/components/NetworkingInterfaces.vue";
import NetworkingRoutes from "@/components/NetworkingRoutes.vue";
import TaskSkeleton from "@/components/tasks/TaskSkeleton.vue";
import { useTaskFinish } from "@/composables";

const toast = useToast();
const taskFinish = useTaskFinish();

const loading = ref(false);

const state = reactive({
  advancedMode: false,

  networkPorts: [],
  dnsServers: [],

  activeNetworkPort: null,
  activeInterface: null,
});

const selectablePorts = computed(() =>
  state.networkPorts.filter((x) => !x.enslaved),
);

function initializeNetworkConfiguration() {
  axios
    .get("/admin/v1/networking", {
      loading,
      errorContext: "Failed to fetch network configuration",
    })
    .then((response) => {
      const networkPorts = response.data.ports;
      for (const networkPort of networkPorts) {
        for (const networkInterface of networkPort.interfaces) {
          if (
            !Object.prototype.hasOwnProperty.call(networkInterface, "gateway")
          ) {
            networkInterface.gateway = "";
          }
        }
      }

      const dnsServers = response.data.nameservers ?? [];
      state.dnsServers = dnsServers;
      state.networkPorts = networkPorts.sort((a, b) =>
        a.name.localeCompare(b.name),
      );
      state.activeNetworkPort = selectablePorts.value[0];
    });
}

function updateNetwork({ finish = false } = {}) {
  axios
    .post(
      "/admin/v1/networking",
      {
        ports: state.networkPorts,
        nameservers: state.dnsServers,
      },
      {
        loading,
        errorContext: "Failed to update network configuration",
      },
    )
    .then(() => {
      toast("Network configuration updated");

      if (finish) {
        taskFinish("Networking");
      }
      else {
        initializeNetworkConfiguration();
      }
    });
}

function initializeActiveState(networkPort) {
  state.activeNetworkPort = networkPort;
  state.activeInterface = networkPort.interfaces[0];
}

initializeNetworkConfiguration();
watch(
  () => state.activeNetworkPort,
  (value) => {
    initializeActiveState(value);
  },
);
</script>
