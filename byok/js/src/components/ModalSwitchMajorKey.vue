<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>
        Switch the {{ majorKey.alias || majorKey.name }} with the pending major
        key
      </p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <p>
        Please review the pending major key. Once you proceed the
        {{ majorKey.alias || majorKey.name }} will be replaced by the pending
        major key. The {{ majorKey.alias || majorKey.name }} will become the
        pending major key to be used as a temporary backup.
      </p>
      <p class="pending-major-key-text">Pending major key</p>
      <ul class="modal-list">
        <li v-for="(value, key) in pendingMajorKeyFiltered" :key="key">
          {{ apiToReadable[key] }}:
          <span :class="key === 'kcv' ? 'checksum' : 'value'"
            >{{ value }}
          </span>
        </li>
      </ul>
    </template>
    <template #footer>
      <button class="button icon-text-button" @click="$emit('closeModal')">
        <i class="fa fa-times" />
        Close
      </button>
      <button class="button blue-button icon-text-button" @click="handleSwitch">
        <i class="fa fa-check" />
        Switch
      </button>
    </template>
  </modal-base>
</template>

<script>
import ModalBase from "@/components/ModalBase.vue";

let apiToReadable = {
  kcv: "Checksum",
  type: "Type",
};

export default {
  components: {
    "modal-base": ModalBase,
  },
  inject: ["getSessionId", "isGpMode"],
  props: {
    pendingMajorKey: {
      type: Object,
      required: true,
    },
    majorKey: {
      type: Object,
      required: true,
    },
  },
  data: function () {
    return {
      apiToReadable: apiToReadable,
    };
  },
  computed: {
    pendingMajorKeyFiltered: function () {
      let filtered = {};
      for (let key in this.pendingMajorKey) {
        if (apiToReadable[key]) {
          filtered[key] = this.pendingMajorKey[key];
        }
      }
      return filtered;
    },
  },
  methods: {
    handleSwitch: function () {
      let url = `/clusters/sessions/${this.getSessionId()}/major-keys/${
        this.majorKey.name
      }/switch`;
      this.$httpV2
        .post(
          url,
          {},
          {
            errorContextMessage: `Failed to switch the ${this.majorKey.name} with the pending major key`,
          },
        )
        .finally(() => {
          this.$emit("refreshMajorKeys");
          this.$emit("closeModal");
        });
    },
  },
};
</script>

<style scoped>
.value {
  color: var(--text-color-blue-lighter);
}

.modal-list {
  margin-bottom: 0;
  padding-left: 1rem;
}

.pending-major-key-text {
  margin-bottom: 0.25rem;
  font-weight: 500;
}
</style>
