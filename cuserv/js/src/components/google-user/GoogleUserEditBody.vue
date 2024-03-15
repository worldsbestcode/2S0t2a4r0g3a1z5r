<template>
  <GoogleUserFormInputs
    v-model:name="state.name"
    v-model:email="state.email"
    v-model:whitelisted="state.whitelisted"
  />

  <ModalFooter
    text="EDIT USER"
    :loading="loading"
    @action="editUser"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, defineProps, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

import ModalFooter from "$shared/components/ModalFooter.vue";

import GoogleUserFormInputs from "@/components/google-user/GoogleUserFormInputs.vue";

const route = useRoute();
const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const loading = ref(false);

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
});

const state = reactive({
  name: props.user.objInfo.name,
  email: props.user.email,
  whitelisted: props.user.whitelisted,
});

const userUuid = computed(() => route.params.userUuid);

function editUser() {
  axios
    .patch(
      `/gcse/v1/users/${userUuid.value}`,
      {
        name: state.name,
        email: state.email,
        whitelisted: state.whitelisted,
      },
      {
        errorContext: "Failed to edit Google CSE user",
        emit: "updateUser",
        loading,
      },
    )
    .then(() => {
      toast("Google CSE user edited");
      emit("finished");
    });
}
</script>
