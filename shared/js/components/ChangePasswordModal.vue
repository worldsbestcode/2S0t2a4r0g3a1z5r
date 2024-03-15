<template>
  <Modal :title="`Change ${props.user}'s password`">
    <template #button="{ on }">
      <ChcButton secondary small v-on="on">Change password</ChcButton>
    </template>
    <template #content="{ toggleModal }">
      <form @submit.prevent="changePassword(toggleModal)">
        <ChcInput
          v-model="state.password"
          label="Current Password"
          placeholder="Current password"
          type="password"
          autofill="current-password"
        />

        <ChcInput
          v-model="state.newPassword"
          label="New Password"
          placeholder="New password"
          type="password"
          autofill="new-password"
        />

        <ChcInput
          v-model="state.confirmNewPassword"
          label="Confirm New Password"
          placeholder="Confirm new password"
          type="password"
          autofill="new-password"
        />

        <ModalFooter :loading="loading" text="CHANGE" @cancel="toggleModal" />
      </form>
    </template>
  </Modal>
</template>

<script setup>
import { defineProps, reactive } from "vue";
import { useToast } from "vue-toastification";
import { useStore } from "vuex";

import axios from "$shared/axios.js";
import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import Modal from "$shared/components/Modal.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";
import { unwrapErr } from "$shared/utils/web";

const toast = useToast();
const store = useStore();

const props = defineProps({
  user: {
    type: String,
    required: true,
  },
});

const state = reactive({
  currentPassword: "",
  newPassword: "",
  confirmNewPassword: "",
});

function changePassword(toggleModal) {
  if (state.newPassword !== state.confirmNewPassword) {
    toast.error(
      "Failed to change password: new password confirmation does not match new password."
    );
    return;
  }

  // different web apps have differnt behaviors
  // todo: Add loading
  axios
    .post("/home/v1/changepw", {
      username: props.user,
      oldPassword: btoa(state.password),
      newPassword: btoa(state.newPassword),
    })
    .then((response) => {
      store.commit("auth/login", response.data);

      state.password = "";
      state.newPassword = "";
      state.confirmNewPassword = "";

      toggleModal();
      toast.success("Password changed");
    })
    .catch((error) => {
      toast.error(unwrapErr(error));
    });
}
</script>
