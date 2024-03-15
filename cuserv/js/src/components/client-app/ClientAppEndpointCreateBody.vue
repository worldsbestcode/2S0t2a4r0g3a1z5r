<template>
  <ChcInput
    v-model="state.identityName"
    hint="optional"
    label="Name"
    placeholder="Name"
  />

  <ChcLabel v-if="templateEndpoints.length > 1" label="Type" div>
    <ChcButton
      v-for="endpoint in templateEndpoints"
      :key="endpoint.name"
      :outline="state.endpointName !== endpoint.name"
      @click="state.endpointName = endpoint.name"
    >
      {{ endpoint.name }}
    </ChcButton>
  </ChcLabel>

  <ChcInput
    v-model="state.deviceAddress"
    hint="address endpoint will use to access this server"
    label="CryptoHub Hostname"
    placeholder="CryptoHub hostname"
  />

  <ChcSelect v-model="state.platform" label="Platform">
    <option
      v-for="templatePlatform in state.templatePlatforms"
      :key="templatePlatform.platform"
      :value="templatePlatform.platform"
    >
      {{ templatePlatform.description }}
    </option>
  </ChcSelect>

  <ModalFooter
    :loading="loading"
    text="ADD ENDPOINT"
    @action="createEndpoint"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, inject, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcSelect from "$shared/components/ChcSelect.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

import { downloadEndpointFile } from "@/components/client-app/client-app.js";

const route = useRoute();
const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const templateData = inject("templateData");

const loading = ref(false);

const state = reactive({
  deviceAddress: "",
  endpointName: "",
  identityName: "",
  platform: "",

  templatePlatforms: [],
});

const serviceUuid = computed(() => route.params.serviceUuid);

const templateEndpoints = computed(() => templateData.value?.params?.endpoints);

function createEndpoint() {
  axios
    .post(
      "/cuserv/v1/clientapp/endpoint",
      {
        serviceUuid: serviceUuid.value,
        endpointName: state.endpointName,
        deviceAddress: state.deviceAddress,
        identityName: state.identityName,
        platform: state.platform,
      },
      {
        errorContext: "Failed to create endpoint",
        emit: "updateEndpoints",
        loading,
      },
    )
    .then((response) => {
      downloadEndpointFile(
        response.data.endpointFiles,
        state.endpointName,
        response.data.result.objInfo.name,
      );

      emit("finished");
      toast("Endpoint created");
    });
}

axios
  .get("/cuserv/v1/clientapp/endpoint/platforms", {
    params: { clientLib: templateData.value.params.clientLib.library },
  })
  .then((response) => {
    state.templatePlatforms = response.data.platforms;
    state.platform = response.data.platforms[0].platform;
  });

state.deviceAddress = window.location.hostname;
state.endpointName = templateEndpoints.value.map((x) => x.name)[0];
</script>
