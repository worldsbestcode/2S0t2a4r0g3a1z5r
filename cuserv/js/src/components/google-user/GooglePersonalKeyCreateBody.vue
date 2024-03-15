<template>
  <div>
    Are you sure you want to continue? This will expire all other active keys.
  </div>

  <ModalFooter
    text="ROTATE KEYS"
    :loading="loading"
    @action="rotateKeys"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { defineEmits, defineProps, ref } from "vue";
import { useToast } from "vue-toastification";

import ModalFooter from "$shared/components/ModalFooter.vue";

const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const props = defineProps({
  serviceUuid: {
    type: String,
    required: true,
  },
  email: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

function rotateKeys() {
  axios
    .post(
      `/gcse/v1/keys`,
      {
        service_uuid: props.serviceUuid,
        email: props.email,
      },
      {
        errorContext: "Failed to rotate keys",
        emit: "updatePersonalKeys",
        loading,
      },
    )
    .then(() => {
      toast("Keys rotated");
      emit("finished");
    });
}
</script>
