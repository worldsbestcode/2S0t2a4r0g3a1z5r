<template>
  <div class="wizard-page-container">
    <div class="wizard-page-name">Select Key Injection Service</div>
    <div class="wizard-page-description"></div>
    <DKIFuzzyInput
      v-model:objectUuid="serviceUuid"
      v-model:objectName="serviceName"
      v-model:data="state.pedInjectServices"
      :get-object-uuid="
        (service) => {
          return service.objInfo.uuid;
        }
      "
      :get-object-name="
        (service) => {
          return service.objInfo.name;
        }
      "
      :focus="registerFocus"
      placeholder="type or scan service name/barcode"
      no-search-results="No key injection services found"
      @objectSelected="emit('serviceSelected')"
    />
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

const emit = defineEmits([
  "update:serviceUuid",
  "update:serviceName",
  "serviceSelected",
]);

const props = defineProps({
  serviceUuid: {
    type: String,
    required: true,
  },
  serviceName: {
    type: String,
    required: true,
  },
});

const loading = ref(false);
const state = reactive({
  pedInjectServices: [],
});

const serviceUuid = computed({
  get() {
    return props.serviceUuid;
  },
  set(value) {
    emit("update:serviceUuid", value);
  },
});

const serviceName = computed({
  get() {
    return props.serviceName;
  },
  set(value) {
    emit("update:serviceName", value);
  },
});
const registerFocus = "DKIServiceSelectorFocus";
const focusMethod = ref(null);

function focusInput(method) {
  focusMethod.value = method;
}

provide(registerFocus, focusInput);
function queryServices() {
  try {
    axios
      .get("/cuserv/v1/services/stubs", {
        params: {
          page: 1,
          pageSize: 100,
        },
        errorContext: "Failed to fetch PED inject services",
        loading,
      })
      .then((response) => {
        state.pedInjectServices = response.data.results.filter((service) => {
          return service.type === "PedInjection";
        });
      });
  } catch (error) {
    console.error(error);
  }
}
onMounted(() => {
  if (focusMethod.value) {
    focusMethod.value();
  }
  // incase the user presses the previous button
  serviceName.value = "";
  serviceUuid.value = "";
  queryServices();
});
</script>
