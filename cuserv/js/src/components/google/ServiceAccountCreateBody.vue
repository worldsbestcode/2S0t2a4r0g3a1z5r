<template>
  <ChcInput
    v-model="state.serviceAccount"
    hint="optional, length 1-64"
    label="Google Cloud Service Account"
    placeholder="service-{number}@gcp-sa-ekms.iam.gserviceaccount.com"
  />

  <ModalFooter
    :loading="loading"
    text="ADD GOOGLE CLOUD SERVICE ACCOUNT"
    @action="addServiceAccount"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { defineEmits, defineProps, reactive, ref } from "vue";
import { useToast } from "vue-toastification";

import ChcInput from "$shared/components/ChcInput.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const props = defineProps({
  serviceUuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  serviceAccount: "",
});

function addServiceAccount() {
  axios
    .post(
      `/gekms/v1/accounts/${props.serviceUuid}/${state.serviceAccount}`,
      {},
      {
        errorContext: "Failed to add Google Cloud Service Account",
        emit: "updateServiceAccounts",
        loading,
      },
    )
    .then(() => {
      toast("Google Cloud service account created");
      emit("finished");
    });
}
</script>
