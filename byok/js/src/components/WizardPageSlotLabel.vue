<template>
  <ul class="wizard-page-list">
    <li>
      <span>Label <span class="hint">(Optional)</span></span>
      <input v-model="label" maxlength="64" class="input input-wide" />
    </li>
  </ul>
</template>

<script>
import { validLabel } from "@/utils/models.js";

export default {
  title: "Slot Label",
  description: "Choose a slot label (optional)",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      label: {
        wizardSummaryText: "Label",
        value: "",
      },
    };
  },
  computed: {
    wizardContinueButtonDisabled: function () {
      return !validLabel(this.label);
    },
  },
  watch: {
    wizardContinueButtonDisabled: function (newValue) {
      this.$emit("wizardContinueButtonDisabled", newValue);
    },
  },
  mounted: function () {
    this.$emit(
      "wizardContinueButtonDisabled",
      this.wizardContinueButtonDisabled,
    );
  },
};
</script>
