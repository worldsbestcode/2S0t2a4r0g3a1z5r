<template>
  <div class="slot">
    <DKIKeyInput v-model:fx-key="state.selectedKey" title="Key" />
    <ChcSpinner
      v-if="keySelected"
      v-model:modelValue="keySlotReference.slot"
      title="Slot"
      :step="1"
      :max="state.maxSlot"
      :min="state.minSlot"
    />
    <DKIKeySlotOptions
      v-if="keySelected && hasOptions"
      v-model:keySlotRef="keySlotReference"
      :protocol="props.protocol"
      :key-type="state.selectedKey.eKeyType"
    />
  </div>
  <div class="modal-button-bottom">
    <button class="button-secondary" @click="emit('cancel')">CANCEL</button>
    <button class="button-primary" @click="createKeySlot">
      {{ editText }}
    </button>
  </div>
</template>

<script setup>
import axios from "axios";
import {
  computed,
  defineEmits,
  defineProps,
  onMounted,
  reactive,
  watch,
} from "vue";
import { useToast } from "vue-toastification";

import ChcSpinner from "$shared/components/ChcSpinner.vue";
import { FXKey, KeyRestrictionSet } from "$shared/utils/keys.js";
import {
  eProtocols,
  generateDefaultKeyOptionsForProtocol,
} from "$shared/utils/protocol.js";

import DKIKeyInput from "@/components/dki/DKIKeyInput.vue";
import DKIKeySlotOptions from "@/components/dki/DKIKeySlotOptions.vue";
import { eHttpsResponse } from "@/misc.js";

const toast = useToast();
const emit = defineEmits(["finished", "cancel"]);
const props = defineProps({
  serviceUuid: {
    type: String,
    required: true,
  },
  keySlotUuid: {
    type: String,
    requried: false,
    default: "",
  },
  restrictedKeys: {
    type: KeyRestrictionSet,
    required: true,
  },
  protocol: {
    type: Number,
    requried: false,
    default: eProtocols.eProtocolNone,
  },
  keySlotInfo: {
    type: Object,
    required: false,
    default: null,
  },
  edit: {
    type: Boolean,
    requried: true,
  },
});

const editText = props.edit ? "UPDATE" : "CREATE";
const keySlotReference = reactive({
  keyUuid: null,
  name: "",
  slot: 0,
  required: false,
  serviceUuid: "",
  options: generateDefaultKeyOptionsForProtocol(props.protocol),
});

function updateSlotInfo() {
  const eKeyType = state.selectedKey.eKeyType;
  let keyTypeSlotInfo = props.keySlotInfo[String(eKeyType)];

  if (keyTypeSlotInfo === undefined) {
    state.hasKeyRefOptions = false;
    state.minSlot = 0;
    state.maxSlot = 255;
  } else {
    state.hasKeyRefOptions = keyTypeSlotInfo.hasKeyRefOptions;
    state.minSlot = keyTypeSlotInfo.minSlot;
    state.maxSlot = keyTypeSlotInfo.maxSlot;
  }
}
watch(keySlotReference, () => {
  updateSlotInfo();
});

const state = reactive({
  hasKeyRefOptions: false,
  minSlot: 0,
  maxSlot: 255,
  selectedKey: new FXKey(),
});

watch(state, () => {
  keySlotReference.keyUuid = state.selectedKey.uuid;
  keySlotReference.name = state.selectedKey.name;
});

const keySelected = computed(() => {
  return keySlotReference.keyUuid;
});

const hasOptions = computed(() => {
  return state.hasKeyRefOptions;
});

function validateKeySlotInfo() {
  let bOk = true;
  if (!state.selectedKey.name) {
    bOk = false;
    toast.error("Key Slot name cannot be empty.");
  }

  if (bOk && !state.selectedKey.uuid) {
    bOk = false;
    toast.error("No key was selected for slot.");
  }

  return bOk;
}

function handleResponse(response) {
  if (response.status == eHttpsResponse.Ok) {
    if (props.edit) {
      toast("Successfully updated key slot");
    } else {
      toast("Successfully create key slot");
    }
    emit("finished");
  }
}

function modifyKeySlot() {
  axios
    .patch(`/dki/v1/keyslots/${props.keySlotUuid}`, keySlotReference)
    .then((response) => {
      handleResponse(response);
    });
}

function createKeySlot() {
  if (validateKeySlotInfo()) {
    if (props.edit) {
      modifyKeySlot();
    } else {
      axios.post("/dki/v1/keyslots", keySlotReference).then((response) => {
        handleResponse(response);
      });
    }
  }
}

function getKeyInfo(uuid) {
  axios
    .post(
      "/dki/v1/keys/query",
      {
        keyUuid: uuid,
      },
      {
        errorContext: "Failed to query keys",
      },
    )
    .then((response) => {
      if (response.status === eHttpsResponse.Ok) {
        let keyInfo = response.data?.keys ? response.data.keys[0] : null;

        if (keyInfo) {
          state.selectedKey = new FXKey(
            keyInfo.uuid,
            keyInfo.name,
            keyInfo.type,
            keyInfo.length,
          );

          updateSlotInfo();
        }
      }
    });
}
function getKeySlotInfo() {
  axios
    .get(`/dki/v1/keyslots/${props.keySlotUuid}`, {
      errorContext: "Failed to fetch key slot reference",
    })
    .then((response) => {
      if (response.status === eHttpsResponse.Ok) {
        let keySlot = response.data;
        if (keySlot) {
          keySlotReference.name = keySlot.objInfo.name;
          keySlotReference.keyUuid = keySlot.keyUuid;
          keySlotReference.serviceUuid = keySlot.serviceUuid;
          keySlotReference.slot = keySlot.slot;
          keySlotReference.required = keySlot.required;
          keySlotReference.options = keySlot.options;
          getKeyInfo(keySlot.keyUuid);
        }
      }
    });
}

onMounted(() => {
  if (props.edit) {
    getKeySlotInfo();
  }

  keySlotReference.serviceUuid = props.serviceUuid;
});
</script>

<style scoped>
.slot {
  width: 100%;
  margin-bottom: 3rem;
}

.modal-button-bottom {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  justify-content: space-between;
}
</style>
