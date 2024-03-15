<template>
  <ChcToggle
    v-model="state.expireExisting"
    label="Replace current credential"
  />

  <ModalFooter
    :loading="loading"
    text="ADD CREDENTIAL"
    @action="createCredential"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, inject, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

import ChcToggle from "$shared/components/ChcToggle.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

import { downloadEndpointFile } from "@/components/client-app/client-app.js";

const route = useRoute();
const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const endpointData = inject("endpointData");

const loading = ref(false);

const state = reactive({
  expireExisting: false,
});
const endpointUuid = computed(() => route.params.endpointUuid);

function createCredential() {
  axios
    .post(
      `/cuserv/v1/clientapp/endpoint/renew/${endpointUuid.value}`,
      {
        expireExisting: state.expireExisting,
      },
      {
        errorContext: "Failed to add credential",
        // endpoint GET is what gives us credentials
        emit: "updateEndpoint",
        loading,
      },
    )
    .then((response) => {
      downloadEndpointFile(
        response.data.endpointFiles,
        endpointData.value.endpointName,
        endpointData.value.objInfo.name,
      );
      emit("finished");
      toast("Credential added");
    });
}
</script>
