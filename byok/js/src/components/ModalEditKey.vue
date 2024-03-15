<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>Edit Key - Slot {{ keySlot }}</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <div class="edit-key-section">
        <p>Label</p>
        <input
          v-model="label"
          maxlength="64"
          class="input input-wide"
          :disabled="immutable"
        />
      </div>

      <div class="edit-key-section">
        <p>Security Usage</p>
        <label v-for="x in securityUsages" :key="x" class="label-checkbox">
          <input
            v-model="securityUsage"
            type="checkbox"
            :value="x"
            :disabled="disableSecurityUsage(x)"
          />
          {{ x }}
        </label>
      </div>

      <div v-if="currentKey.type !== 'Certificate'" class="edit-key-section">
        <p>Usage</p>
        <label v-for="x in usages" :key="x" class="label-checkbox">
          <input
            v-model="usage"
            type="checkbox"
            :value="x"
            :disabled="disableUsage(x)"
          />
          {{ x }}
        </label>
      </div>
    </template>
    <template #footer>
      <button class="button icon-text-button" @click="$emit('closeModal')">
        <i class="fa fa-times" />
        Cancel
      </button>
      <button
        :disabled="invalidLabel"
        class="button blue-button icon-text-button"
        @click="handleEditKey"
      >
        <i class="fa fa-check icon-right" />
        Edit
      </button>
    </template>
  </modal-base>
</template>

<script>
import {
  getSecurityUsages,
  getUsages,
  getValidUsages,
  disableUsage,
  validLabel,
} from "@/utils/models.js";
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
    currentKey: {
      type: Object,
      required: true,
    },
  },
  data: function () {
    return {
      label: this.currentKey.label,
      securityUsage: this.currentKey.securityUsage,
      usage: this.currentKey.usage,
    };
  },
  computed: {
    securityUsages: function () {
      return getSecurityUsages(this.currentKey.type);
    },
    usages: function () {
      return getUsages(this.currentKey.type);
    },
    validUsages: function () {
      return getValidUsages({
        type: this.currentKey.type,
        gpMode: this.isGpMode(),
        modifier: this.currentKey.modifier,
      });
    },
    immutable: function () {
      return this.securityUsage.includes("Immutable");
    },
    invalidLabel: function () {
      return !validLabel(this.label);
    },
  },
  methods: {
    disableSecurityUsage: function (x) {
      if (x === "Immutable") {
        return false;
      } else {
        return this.immutable;
      }
    },
    disableUsage: function (usageValue) {
      return disableUsage({
        usageValue: usageValue,
        usage: this.usage,
        validUsages: this.validUsages,
        immutable: this.immutable,
      });
    },
    handleEditKey: function () {
      let url = `/clusters/sessions/${this.getSessionId()}/keytable`;
      if (!this.isGpMode()) {
        url += `/${this.type.toLowerCase()}`;
      }
      url += `/${this.keySlot}`;
      let body = {
        label: this.label,
        securityUsage: this.securityUsage,
        usage: this.usage,
      };
      this.$httpV2
        .patch(url, body, { errorContextMessage: "Failed to edit key" })
        .finally(() => {
          this.$emit("refreshTable");
          this.$emit("closeModal");
        });
    },
  },
};
</script>

<style scoped>
.edit-key-section + .edit-key-section {
  margin-top: 0.5rem;
}

.edit-key-section > p {
  font-weight: 500;
  font-size: 18px;
  margin-bottom: 0.2rem;
}

.edit-key-section label + label {
  margin-left: 0.5rem;
}
</style>
