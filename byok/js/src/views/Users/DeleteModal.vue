<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>Delete User - {{ username }}</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <p class="delete-header">Are you sure?</p>
      <p class="delete-message">
        Are you sure you want to delete {{ username }}? This action cannot be
        undone.
      </p>
    </template>
    <template #footer>
      <button class="button icon-text-button" @click="$emit('closeModal')">
        <i class="fa fa-times" />
        Close
      </button>
      <button class="button blue-button icon-text-button" @click="deleteUser">
        <i class="fa fa-check" />
        Delete
      </button>
    </template>
  </modal-base>
</template>

<script>
import ModalBase from "@/components/ModalBase.vue";

export default {
  name: "DeleteModal",
  components: {
    "modal-base": ModalBase,
  },
  inject: ["getSessionId"],
  props: {
    username: {
      type: String,
      required: true,
    },
  },
  methods: {
    deleteUser: function () {
      let url = `/clusters/sessions/${this.getSessionId()}/identities/${
        this.username
      }`;
      this.$httpV2
        .delete(url, {
          errorContextMessage: `Failed to delete identity "${this.username}"`,
        })
        .finally(() => {
          this.$emit("closeModal");
        });
    },
  },
};
</script>

<style scoped>
.delete-header {
  font-size: 18px;
  margin-bottom: 0.25rem;
}

.delete-message {
  margin: 0;
}
</style>
