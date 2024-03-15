<template>
  <modal-base @keyup.enter="submitPassword" @esc="$emit('closeModal')">
    <template #header>
      <p>Change Password - {{ username }}</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <ul class="wizard-page-list">
        <li>
          <span>Current password</span>
          <input
            v-model="currentPassword"
            type="password"
            class="input input-wide"
          />
        </li>
        <li>
          <span>New password</span>
          <input
            v-model="newPassword"
            type="password"
            class="input input-wide"
          />
        </li>
        <li>
          <span>Confirm new password</span>
          <input
            v-model="confirmPassword"
            type="password"
            class="input input-wide"
          />
        </li>
      </ul>
    </template>
    <template #footer>
      <button class="button icon-text-button" @click="$emit('closeModal')">
        <i class="fa fa-times" />
        Close
      </button>
      <button
        class="button blue-button icon-text-button"
        @click="submitPassword"
      >
        <i class="fa fa-check" />
        Change
      </button>
    </template>
  </modal-base>
</template>

<script>
import ModalBase from "@/components/ModalBase.vue";

export default {
  name: "ChangePasswordModal",
  components: {
    "modal-base": ModalBase,
  },
  props: {
    username: {
      type: String,
      required: true,
    },
    sessionId: {
      type: String,
      required: true,
    },
  },
  data: function () {
    return {
      currentPassword: null,
      newPassword: null,
      confirmPassword: null,
    };
  },
  methods: {
    submitPassword: async function () {
      let message;
      let payload = {};
      if (!this.newPassword) {
        message = "Password required";
      } else if (this.newPassword.length < 6) {
        message = "Password must be 6 characters";
      } else if (!this.confirmPassword) {
        message = "Confirm password";
      } else if (this.newPassword !== this.confirmPassword) {
        message = "Passwords do not match";
      } else {
        payload.password = btoa(this.newPassword);
        if (this.currentPassword) {
          payload.oldPassword = btoa(this.currentPassword);
        }
      }
      this.currentPassword = null;
      this.newPassword = null;
      this.confirmPassword = null;
      if (message) {
        this.$bus.emit("toaster", { message, type: "error" });
        return;
      }

      const url =
        "/clusters/sessions/" +
        this.sessionId +
        "/identities/" +
        this.username +
        "/change-password";
      this.$httpV2
        .post(url, payload, {
          errorContextMessage: "Failed to change password",
        })
        .then(() => {
          this.$bus.emit("toaster", {
            message: "Password successfully changed",
            type: "success",
          });
          this.$emit("closeModal");
        });
    },
  },
};
</script>
