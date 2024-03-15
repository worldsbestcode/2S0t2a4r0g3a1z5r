<template>
  <div class="joint-inputs">
    <select v-model="state.authType" style="flex-grow: 1" class="chc-input">
      <option v-for="authType in props.endpoint.authType" :key="authType">
        {{ authType }}
      </option>
    </select>
    <select v-model="state.authMechanismUuid" class="chc-input">
      <option>Default</option>
      <option
        v-for="authMechanism in props.authMechanisms.filter(
          (x) => x.authType === state.authType,
        )"
        :key="authMechanism.uuid"
        :value="authMechanism.uuid"
      >
        {{ authMechanism.name }} - {{ authMechanism.idpName }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { defineEmits, defineProps, reactive, watch, watchEffect } from "vue";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  endpoint: {
    type: Object,
    required: true,
  },
  authMechanisms: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: Object,
    required: true,
  },
});

const state = reactive({
  authType: null,
  authMechanismUuid: null,
});

watch(
  () => state.authType,
  () => {
    state.authMechanismUuid = "Default";
  },
);

watchEffect(() => {
  const ret = {
    type: state.authType,
  };

  if (state.authMechanismUuid === "Default") {
    ret.default = true;
  } else {
    ret.uuid = state.authMechanismUuid;
  }

  emit("update:modelValue", ret);
});

const defaultPrecedences = ["ApiKey", "UserPass", "TlsBundle"];

for (const authType of defaultPrecedences) {
  if (props.endpoint.authType.find((x) => x === authType)) {
    state.authType = authType;
    break;
  }
}
</script>

<style scoped>
.joint-inputs {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 12px;
}

.joint-inputs .chc-input {
  width: initial;
  min-width: initial;
}
</style>
