<template>
  <div>Are you sure you want to continue? This action cannot be reversed.</div>

  <ModalFooter
    :loading="loading"
    text="DELETE"
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
  keyUuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

function deleteKey() {
  axios
    .post(
      `/gekms/gapi/v0/keys/${props.keyUuid}:destroyKey`,
      {
        key_path: props.keyUuid,
      },
      {
        errorContext: "Failed to delete key",
        emit: "updateCryptospaceKeys",
        loading,
      },
    )
    .then(() => {
      toast("Key deleted");
      emit("finished");
    });
}
</script>
