<template>
  <ChcLabel div label="Bonding">
    <ChcLabel div class="modal-stuff-container">
      <ChcLabel v-if="bondNetworkPorts.length > 0" div label="Existing bonds">
        <!-- todo: Make a table for this -->
        <div
          v-for="bondNetworkPort of bondNetworkPorts"
          :key="bondNetworkPort.name"
        >
          {{ bondNetworkPort.name }} ({{ bondNetworkPort.slaves.join(", ") }})
          ({{ bondNetworkPort.bondMode }})
          <ChcButton secondary small @click="deleteBonding(bondNetworkPort)">
            Delete
          </ChcButton>
        </div>
      </ChcLabel>

      <template v-if="bondableNetworkPorts.length > 1">
        <ChcInput v-model="state.bondName" label="Bond name" />

        <ChcSelect v-model="state.bondMode" label="Bond mode">
          <option
            v-for="bondModeOption in bondModeOptions"
            :key="bondModeOption"
            :value="bondModeOption"
          >
            {{ bondModeOption }}
          </option>
        </ChcSelect>

        <ChcLabel div label="Ports to bond">
          <div class="radio-container">
            <ChcRadio
              v-for="bondableNetworkPort of bondableNetworkPorts"
              :key="bondableNetworkPort.name"
              v-model="state.networkPortsToBond"
              :label="bondableNetworkPort.name"
              :value="bondableNetworkPort"
              type="checkbox"
            />
          </div>
        </ChcLabel>

        <ChcLabel div>
          <ChcButton secondary @click="createBonding">Add bonding</ChcButton>
        </ChcLabel>
      </template>
    </ChcLabel>
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps, reactive } from "vue";
import { useToast } from "vue-toastification";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcRadio from "$shared/components/ChcRadio.vue";
import ChcSelect from "$shared/components/ChcSelect.vue";

const bondModeOptions = [
  "round-robin",
  "active-backup",
  "802.3ad-mac",
  "broadcast",
  "802.3ad-lacp",
  "balance-xor",
  "balance-tlb",
];

const toast = useToast();

const emit = defineEmits(["update:networkPorts", "update:activeNetworkPort"]);

const props = defineProps({
  networkPorts: {
    type: Array,
    default: () => [],
  },
  activeNetworkPort: {
    type: Object,
    default: null,
  },
});

const state = reactive({
  bondName: "",
  networkPortsToBond: [],
  bondMode: "active-backup",
});

const networkPorts = computed({
  get() {
    return props.networkPorts;
  },
  set(value) {
    emit("update:networkPorts", value);
  },
});
const activeNetworkPort = computed({
  get() {
    return props.activeNetworkPort;
  },
  set(value) {
    emit("update:activeNetworkPort", value);
  },
});

const bondableNetworkPorts = computed(() =>
  networkPorts.value.filter((x) => !x.bond && !x.enslaved),
);

const bondNetworkPorts = computed(() =>
  networkPorts.value.filter((x) => x.bond),
);

function createBonding() {
  const newNetworkPort = {
    name: state.bondName,
    bond: true,
    bondMode: state.bondMode,
    slaves: state.networkPortsToBond.map((x) => x.name),
    enslaved: false,
    interfaces: [],
    routes: [],
  };

  if (newNetworkPort.name === "") {
    newNetworkPort.name = newNetworkPort.slaves.join("-");
  }

  if (newNetworkPort.slaves.length < 2) {
    toast.error("Bondings require at least two network ports");
    return;
  }

  const newArrayLength = networkPorts.value.push(newNetworkPort);
  activeNetworkPort.value = networkPorts.value[newArrayLength - 1];

  for (const networkPort of state.networkPortsToBond) {
    networkPort.enslaved = true;
    networkPort.interfaces = [];
  }

  // todo: Define defaults somewhere...
  state.bondName = "";
  state.networkPortsToBond = [];
  state.bondMode = "active-backup";
}

function deleteBonding(bondNetworkPort) {
  const bondNetworkPortIndex = networkPorts.value.indexOf(bondNetworkPort);
  networkPorts.value.splice(bondNetworkPortIndex, 1);
  activeNetworkPort.value = networkPorts.value.at(bondNetworkPortIndex - 1);

  const bondedNetworkPorts = bondNetworkPort.slaves.map((networkPortName) =>
    networkPorts.value.find(
      (networkPort) => networkPort.name === networkPortName,
    ),
  );
  for (const networkPort of bondedNetworkPorts) {
    networkPort.enslaved = false;
  }
}
</script>
