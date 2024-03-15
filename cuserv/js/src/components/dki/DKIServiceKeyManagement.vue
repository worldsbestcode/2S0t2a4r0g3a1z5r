<template>
  <div class="wizard-page-container">
    <div class="wizard-page-name">Select Optional Key Slots</div>
    <div class="wizard-page-description">Service: {{ state.serviceName }}</div>
    <DKIFuzzyInput
      v-model:objectUuid="keyUuid"
      v-model:objectName="keyName"
      v-model:data="state.availableKeySlots"
      :get-object-uuid="
        (object) => {
          return object.objInfo.uuid;
        }
      "
      :get-object-name="
        (object) => {
          return 'Slot: ' + object.slot + ' - ' + object.objInfo.name;
        }
      "
      :focus="registerFocus"
      placeholder="type or key slot name/barcode "
      no-search-results="No key slots found"
      @objectSelected="addKey"
    ></DKIFuzzyInput>
    <DKIKeyList
      :keys="selectedKeySlots"
      title="Keys To Be Injected"
      @deleteKey="removeKeyFromOptionalList"
    ></DKIKeyList>
  </div>
</template>

<script setup>
import axios from "axios";
import {
  computed,
  defineEmits,
  defineProps,
  onMounted,
  provide,
  reactive,
  ref,
} from "vue";

import DKIFuzzyInput from "@/components/dki/DKIFuzzyInput.vue";
import DKIKeyList from "@/components/dki/DKIKeyList.vue";

const emit = defineEmits(["update:selectedKeySlots", "update:deviceGroupUuid"]);
const props = defineProps({
  serviceUuid: {
    type: String,
    required: true,
  },
  serviceName: {
    type: String,
    required: true,
  },
  deviceGroupUuid: {
    type: String,
    required: true,
  },
  selectedKeySlots: {
    type: Array,
    requied: true,
  },
});

const registerFocus = "DKIServiceKeyManagement";
const focusKeyMethod = ref(null);

function focusKeyInput(method) {
  focusKeyMethod.value = method;
}
provide(registerFocus, focusKeyInput);

const state = reactive({
  keyName: "",
  keyUuid: "",
  availableKeySlots: [],
  serviceName: props.serviceName,
  useDefault: false,
});
const keyName = computed({
  get() {
    return state.keyName;
  },
  set(value) {
    state.keyName = value;
  },
});

const keyUuid = computed({
  get() {
    return state.keyUuid;
  },
  set(value) {
    state.keyUuid = value;
  },
});

const deviceGroupUuid = computed({
  get() {
    return props.deviceGroupUuid;
  },
  set(value) {
    emit("update:deviceGroupUuid", value);
  },
});

const selectedKeySlots = computed({
  get() {
    let keys = props.selectedKeySlots;
    return keys.sort((a, b) => a.slot - b.slot);
  },
  set(value) {
    emit("update:selectedKeySlots", value);
  },
});

function sortAvailableKeySlots() {
  state.availableKeySlots = state.availableKeySlots.sort(
    (a, b) => a.slot - b.slot,
  );
}
function addKey() {
  let key = findKeyByUuid(state.keyUuid);
  if (key) {
    // check if the key is in the list
    selectedKeySlots.value.push(key);
    state.availableKeySlots = state.availableKeySlots.filter((keySlot) => {
      return key.objInfo.uuid !== keySlot.objInfo.uuid;
    });

    sortAvailableKeySlots();
  }
}

/**
 * Removes the key from the optional list based on the uuid
 */
function removeKeyFromOptionalList(uuid) {
  selectedKeySlots.value = selectedKeySlots.value.filter((key) => {
    let keep = key.objInfo.uuid !== uuid;
    if (!keep) {
      state.availableKeySlots.push(key);
      sortAvailableKeySlots();
    }
    return keep;
  });
}

function findKeyByUuid(keyUuid) {
  for (let keyIndex in state.availableKeySlots) {
    let key = state.availableKeySlots[keyIndex];
    if (key.objInfo.uuid == keyUuid) {
      return key;
    }
  }

  return null;
}

function getKeySlotReferences(keySlotRefIds) {
  axios
    .post(
      "/dki/v1/keyslots/refs",
      {
        uuids: keySlotRefIds,
      },
      {
        errorContext: "Failed to query key slot references",
      },
    )
    .then((response) => {
      let keySlots = [];
      if (response.status === 200) {
        keySlots = response.data?.results ? response.data.results : [];
      }

      keySlots.forEach((slot) => {
        if (slot.required) {
          selectedKeySlots.value.push(slot);
        } else {
          state.availableKeySlots.push(slot);
        }
      });
      sortAvailableKeySlots();
    });
}

function getServiceInfo() {
  try {
    axios
      .get(`/cuserv/v1/services/${props.serviceUuid}`, {
        errorContext: "Failed to fetch PED inject services",
      })
      .then((response) => {
        state.serviceName = response.data.objInfo.name;
        let keySlotRefIds = [];
        response.data.associatedObjects.forEach((associatedObject) => {
          if (associatedObject.purpose === "KeySlotReference") {
            keySlotRefIds.push(associatedObject.associatedUuid);
          } else if (associatedObject.purpose === "DeviceGroup") {
            deviceGroupUuid.value = associatedObject.associatedUuid;
          }
        });
        getKeySlotReferences(keySlotRefIds);
      });
  } catch (error) {
    console.error(error);
  }
}

onMounted(() => {
  if (focusKeyMethod.value) {
    focusKeyMethod.value();
  }
  getServiceInfo();
});
</script>

<style scoped>
.dki-spacer {
  height: 60px;
}

.dki-checkbox {
  text-align: left;
  margin-bottom: 0.4rem;
}
</style>
