<template>
  <ul class="wizard-page-list">
    <li>
      <span>ECC - curve</span>
      <select v-model="curve" class="button button-wide">
        <option :value="null">Select a curve</option>
        <option
          v-for="(name, curve) in eccCurveOidToName"
          :key="curve"
          :value="curve"
        >
          {{ name }}
        </option>
      </select>
    </li>
  </ul>
</template>

<script>
import { eccCurveOidToName } from "@/utils/models.js";

export default {
  title: "Key Information",
  description: "Provide information for the ECC key",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      curve: {
        value: null,
        wizardSummaryText: "Curve",
      },
    };
  },
  data: function () {
    return {
      eccCurveOidToName: eccCurveOidToName,
    };
  },
  computed: {
    wizardContinueButtonDisabled: function () {
      return this.curve === null;
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
