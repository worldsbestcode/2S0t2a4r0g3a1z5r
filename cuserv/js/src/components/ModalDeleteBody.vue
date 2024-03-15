<template>
  <div>Are you sure you want to continue? This action cannot be reversed.</div>

  <ModalFooter
    :loading="loading"
    text="DELETE"
    @action="deleteCallback"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { defineEmits, defineProps, ref } from "vue";
import { useToast } from "vue-toastification";

import ModalFooter from "$shared/components/ModalFooter.vue";

const emit = defineEmits(["finished", "cancel"]);

const toast = useToast();

const props = defineProps({
  url: {
    type: String,
    required: true,
  },
  error: {
    type: String,
    required: true,
  },
  axiosEmit: {
    type: String,
    default: undefined,
  },
  success: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

function deleteCallback() {
  axios
    .delete(props.url, {
      errorContext: props.error,
      emit: props.axiosEmit,
      loading,
    })
    .then(() => {
      toast(props.success);
      emit("finished");
    });
}
</script>
