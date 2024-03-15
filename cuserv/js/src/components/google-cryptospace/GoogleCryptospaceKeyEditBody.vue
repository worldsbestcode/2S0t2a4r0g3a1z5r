<template>
  <GoogleCryptospaceKeyFormInputs
    v-model:justifications="state.justifications"
    v-model:name="state.name"
    v-model:rotationPeriod="state.rotationPeriod"
  />

  <ModalFooter
    :loading="loading"
    text="EDIT KEY"
    @action="editKey"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { defineEmits, defineProps, reactive, ref } from "vue";
import { useToast } from "vue-toastification";

import ModalFooter from "$shared/components/ModalFooter.vue";

import GoogleCryptospaceKeyFormInputs from "@/components/google-cryptospace/GoogleCryptospaceKeyFormInputs.vue";

const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const props = defineProps({
  keyInformation: {
    type: Object,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  name: props.keyInformation.objInfo.name,
  justifications: props.keyInformation.justifications,
  rotationPeriod: props.keyInformation.rotationPeriod,
});

function editKey() {
  axios
    .patch(
      `/gekms/v1/keys/${props.keyInformation.objInfo.uuid}`,
      {
        name: state.name,
        justifications: state.justifications,
        rotation_period: state.rotationPeriod,
      },
      {
        errorContext: "Failed to edit key",
        emit: "updateCryptospaceKey",
        loading,
      },
    )
    .then(() => {
      toast("Key edited");
      emit("finished");
    });
}
</script>
