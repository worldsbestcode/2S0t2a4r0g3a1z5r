<template>
  <ChcLabel div>
    <ChcButton
      style="margin-top: 1rem; display: block"
      secondary
      @click="createInterface"
    >
      Create new interface
    </ChcButton>
  </ChcLabel>

  <ChcLabel v-if="activeInterface" div class="modal-stuff-container">
    <ChcInput v-model="activeInterface.name" label="Interface Name" />

    <ChcToggle v-model="activeInterface.dynamic" label="DHCP" />

    <ChcInput
      v-model="activeInterface.ip"
      label="IP"
      :hint="isDhcp ? 'Read only' : null"
      :readonly="isDhcp"
    />
    <ChcInput
      v-model="activeInterface.netmask"
      label="Netmask"
      :hint="isDhcp ? 'Read only' : null"
      :readonly="isDhcp"
    />
    <ChcInput
      v-model="activeInterface.gateway"
      label="Gateway"
      :hint="isDhcp ? 'Read only' : null"
      :readonly="isDhcp"
    />

    <ChcLabel div>
      <ChcButton secondary @click="deleteActiveInterface">
        Delete interface
      </ChcButton>
    </ChcLabel>
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";
import { useToast } from "vue-toastification";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";

const toast = useToast();

const emit = defineEmits(["update:modelValue", "update:interfaces"]);

const props = defineProps({
  modelValue: {
    type: Object,
    default: undefined,
  },
  interfaces: {
    type: Array,
    required: true,
  },
  networkPortName: {
    type: String,
    required: true,
  },
});

const isDhcp = computed(() => activeInterface.value?.dynamic);

const activeInterface = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});
const interfaces = computed({
  get: () => props.interfaces,
  set: (value) => emit("update:interfaces", value),
});

function createInterface() {
  const newInterface = { name: "", dynamic: false, ip: "", netmask: "" };
  const newArrayLength = interfaces.value.push(newInterface);
  newInterface.name = `${props.networkPortName}-${newArrayLength}`;
  newInterface.name = newInterface.name.replace(/\s+/g, "");
  activeInterface.value = interfaces.value[newArrayLength - 1];
}

function deleteActiveInterface() {
  const activeInterfaceIndex = interfaces.value.indexOf(activeInterface.value);
  let nextInterfaceIndex = activeInterfaceIndex - 1;
  if (activeInterfaceIndex === 0) {
    nextInterfaceIndex = 0;
  }

  interfaces.value.splice(activeInterfaceIndex, 1);
  activeInterface.value = interfaces.value[nextInterfaceIndex];

  // Not quite clear something was deleted without a toast
  toast("Deleted active interface");
}
</script>
