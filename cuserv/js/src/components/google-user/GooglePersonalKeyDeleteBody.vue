<template>
  <div>Are you sure you want to continue? This action cannot be reversed.</div>

  <ModalFooter
    text="DELETE"
    :loading="loading"
    @action="deleteKey"
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
  keyUuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

function deleteKey() {
  axios
    .delete(`/gcse/v1/keys`, {
      data: {
        service_uuid: props.serviceUuid,
        email: props.email,
        key_uuid: props.keyUuid,
      },
      errorContext: "Failed to delete key",
      emit: "updatePersonalKeys",
      loading,
    })
    .then(() => {
      toast("Key deleted");
      emit("finished");
    });
}
</script>
