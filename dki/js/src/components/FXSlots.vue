<template>
  <v-container fluid class="fx-slots">
    <usb-terminal-card
      v-for="(device, index) in getDevicesToShow"
      :key="device.id"
      class="mb-1"
      :terminal-id="device.id"
      :index="(page - 1) * pageSize + index"
    />
  </v-container>
</template>

<script setup>
import { computed } from "vue";
import UsbTerminalCard from "@/components/UsbTerminalCard.vue";
import store from "@/store";

const devices = computed(() => {
  return store.getters["pedinject/getDevices"];
});

const page = computed(() => {
  return store.getters["pedinject/getPagination"].page;
});

const pageSize = computed(() => {
  return store.getters["pedinject/getPagination"].pageSize;
});

const getDevicesToShow = computed(() => {
  const start = (page.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return devices.value.slice(start, end);
});
</script>

<style scoped>
.fx-slots {
  display: flex;
  flex-wrap: wrap;
  padding-top: 0;
}
</style>
