<template>
  <GoogleUserFormInputs
    v-model:name="state.name"
    v-model:email="state.email"
    v-model:whitelisted="state.whitelisted"
  />

  <ModalFooter
    text="CREATE GOOGLE USER"
    :loading="loading"
    @action="createGoogleUser"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

import ModalFooter from "$shared/components/ModalFooter.vue";

import GoogleUserFormInputs from "@/components/google-user/GoogleUserFormInputs.vue";

const route = useRoute();
const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const serviceUuid = computed(() => route.params.serviceUuid);

const loading = ref(false);

const state = reactive({
  name: "",
  email: "",
  whitelisted: false,
});

function createGoogleUser() {
  axios
    .post(
      `/gcse/v1/users`,
      {
        name: state.name,
        service_uuid: serviceUuid.value,
        email: state.email,
        whitelisted: state.whitelisted,
      },
      {
        errorContext: "Failed to create Google CSE user",
        emit: "updateUsers",
        loading,
      },
    )
    .then(() => {
      toast("Google CSE user created");
      emit("finished");
    });
}
</script>
