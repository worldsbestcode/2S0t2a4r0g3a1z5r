<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>Delete Key - Slot {{ keySlot }}</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <p class="delete-key-header">Are you sure?</p>
      <p class="delete-key-text">
        Are you sure you want to delete this key? This action cannot be undone.
      </p>
    </template>
    <template #footer>
      <button class="button icon-text-button" @click="$emit('closeModal')">
        <i class="fa fa-times" />
        Cancel
      </button>
      <button
        class="button blue-button icon-text-button"
        @click="handleDeleteKey"
      >
        <i class="fa fa-check icon-right" />
        Delete
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
  inject: ["getSessionId", "isGpMode"],
  props: {
    type: {
      type: String,
      required: false,
    },
    keySlot: {
      type: Number,
      required: true,
    },
  },
  methods: {
    handleDeleteKey: function () {
      let url = `/clusters/sessions/${this.getSessionId()}/keytable`;
      if (!this.isGpMode()) {
        url += `/${this.type.toLowerCase()}`;
      }
      url += `/${this.keySlot}`;
      this.$httpV2
        .delete(url, { errorContextMessage: "Failed to delete key" })
        .finally(() => {
          this.$emit("refreshTable");
          this.$emit("closeModal");
        });
    },
  },
};
</script>

<style scoped>
.delete-key-header {
  font-size: 18px;
  margin-bottom: 0.25rem;
}

.delete-key-text {
  margin-bottom: 0;
}
</style>
