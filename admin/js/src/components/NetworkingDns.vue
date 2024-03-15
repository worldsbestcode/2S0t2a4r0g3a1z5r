<template>
  <ChcLabel div label="DNS" class="modal-stuff-container">
    <div
      v-for="(_, index) of dnsServers"
      :key="index"
      class="dns-server-container"
    >
      <ChcInput v-model="dnsServers[index]" />

      <div class="dns-server-delete-container">
        <!-- todo: Use X icon image -->
        <button class="dns-server-delete" @click="deleteDns(index)">X</button>
      </div>
    </div>
    <ChcButton
      secondary
      style="margin-top: 0.5rem; display: block"
      @click="createDns"
    >
      Add DNS
    </ChcButton>
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: {
    type: Array,
    required: true,
  },
});

const dnsServers = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit("update:modelValue", value);
  },
});

function createDns() {
  dnsServers.value.push("");
}

function deleteDns(index) {
  dnsServers.value.splice(index, 1);
}
</script>

<style scoped>
.dns-server-container {
  position: relative;
}

.dns-server-container + .dns-server-container {
  margin-top: 0.5rem;
}

.dns-server-delete-container {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 40px;

  display: flex;
  justify-content: center;
  align-items: center;
}

.dns-server-delete {
  background: none;
  border: 0;
  padding: 0;
  height: 30px;
  width: 30px;
}
</style>
