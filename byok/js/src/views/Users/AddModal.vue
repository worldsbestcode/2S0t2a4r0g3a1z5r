<template>
  <modal-base @keyup.enter="addIdentity" @esc="$emit('closeModal')">
    <template #header>
      <p>Add user</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <ul class="wizard-page-list">
        <li>
          <span>Username</span>
          <input v-model="username" class="input input-wide" />
        </li>
        <li>
          <span>Password</span>
          <input v-model="password" type="password" class="input input-wide" />
        </li>
        <li>
          <span>Confirm password</span>
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
      <button class="button blue-button icon-text-button" @click="addIdentity">
        <i class="fa fa-check" />
        Add
      </button>
    </template>
  </modal-base>
</template>

<script>
import ModalBase from "@/components/ModalBase.vue";

export default {
  components: {
    "modal-base": ModalBase,
  },
  inject: ["getSessionId"],
  data: function () {
    return {
      username: null,
      password: null,
      confirmPassword: null,
    };
  },
  methods: {
    addIdentity: function () {
      let message;
      if (!this.username) {
        message = "Username required";
      } else if (!this.password) {
        message = "Password required";
      } else if (!this.confirmPassword) {
        message = "Confirm password";
      } else if (this.password !== this.confirmPassword) {
        message = "Passwords don't match";
      }

      if (message) {
        this.$bus.emit("toaster", { message: message });
        return;
      }

      let url = `/clusters/sessions/${this.getSessionId()}/identities`;
      let body = {
        name: this.username,
        roles: ["Key Manager"],
        password: btoa(this.password),
        locked: false,
      };
      this.$httpV2
        .post(url, body, { errorContextMessage: "Failed to create identity" })
        .finally(() => {
          this.$emit("closeModal");
        });
    },
  },
};
</script>
