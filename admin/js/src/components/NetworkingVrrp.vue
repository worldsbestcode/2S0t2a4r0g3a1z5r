<template>
  <ChcLabel div label="VRRP">
    <ChcLabel div class="modal-stuff-container">
      <ChcInput label="Virtual IP" />
      <ChcInput label="Virtual ID" max="99" min="1" type="number" />
      <ChcInput label="Priority" max="255" min="1" type="number" value="100"/>
      <ChcInput label="Advertisement interval seconds" max="99" min="1" type="number" />
      <ChcInput label="Advertisement port" />
      <ChcSelect v-model="state.strategyMode" label="Strategy">
        <option
          v-for="strategyOption in strategyOptions"
          :key="strategyOption"
          :value="strategyOption"
        >
          {{ strategyOption }}
        </option>
      </ChcSelect>
      <ChcSelect v-if="state.strategyMode == 'Device'" v-model="state.deviceList" label="Device Status">
        <option
          v-for="device in deviceList"
          :key="device"
          :value="device"
        >
          {{ device }}
        </option>
      </ChcSelect>
      <ChcInput label="Reclaim Master after 'x' pings"  max="9999" min="0" type="number" />
      <ChcToggle
          v-model="state.advancedMode"
          label="Enable service preemption"
      />
    </ChcLabel>
  </ChcLabel>
</template>

<script setup>
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcSelect from "$shared/components/ChcSelect.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";
import { reactive, onMounted } from "vue";
import axios from "axios";

const state = reactive({
  strategyMode: "Default",
  preemptionMode: false,
  deviceList: []
});

const strategyOptions = ["Default", "Device"];

onMounted(() => {
  axios
    .post(
      "/admin/v1/networking/vrrp-devices",
    )
    .then((res) => res.json())
    .then(data => state.deviceList = data.devices);
})
</script>