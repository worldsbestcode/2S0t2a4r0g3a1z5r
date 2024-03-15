<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>{{ majorKey.alias || majorKey.name }} - Clear</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <p class="delete-key-header">Are you sure?</p>
      <p class="delete-key-text">
        Are you sure you want to clear the major key? This action cannot be
        undone.
      </p>
    </template>
    <template #footer>
      <button class="button icon-text-button" @click="$emit('closeModal')">
        <i class="fa fa-times" />
        Cancel
      </button>
      <button
        class="button blue-button icon-text-button"
        @click="handleClearMajorKey"
      >
        <i class="fa fa-check icon-right" />
        Clear
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
    majorKey: {
      type: Object,
      required: true,
    },
  },
  methods: {
    handleClearMajorKey: function () {
      let url = `/clusters/sessions/${this.getSessionId()}/major-keys/${
        this.majorKey.name
      }`;
      this.$httpV2
        .delete(url, {
          errorContextMessage: `Failed to delete ${this.majorKey.name}`,
        })
        .finally(() => {
          this.$emit("refreshMajorKeys");
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
