<template>
  <div>
    <div v-if="!securityUsageHidden" class="wizard-success-div">
      <p>Security Usage</p>
      <label v-for="x in securityUsages" :key="x" class="label-checkbox">
        <input v-model="securityUsage" type="checkbox" :value="x" />
        {{ x }}
      </label>
    </div>
    <div class="wizard-success-div">
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
  </div>
</template>

<script>
import {
  getSecurityUsages,
  getUsages,
  getValidUsages,
  disableUsage,
} from "@/utils/models.js";

export default {
  inject: ["isGpMode"],
  title: "Key Usage and Security Usage",
  description: "Select the key usage and security usage",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      securityUsage: {
        value: [],
        wizardSummaryText: "Security usage",
      },
      usage: {
        value: [],
        wizardSummaryText: "Usage",
      },
    };
  },
  props: {
    keyType: {
      type: [String, Function],
      required: true,
    },
    keyModifier: {
      type: Function,
      default: () => {},
    },
    securityUsageHidden: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    _keyType: function () {
      return typeof this.keyType === "function" ? this.keyType() : this.keyType;
    },
    securityUsages: function () {
      return getSecurityUsages(this._keyType);
    },
    usages: function () {
      return getUsages(this._keyType);
    },
    validUsages: function () {
      return getValidUsages({
        type: this._keyType,
        gpMode: this.isGpMode(),
        modifier: this.keyModifier(),
      });
    },
  },
  mounted: function () {
    this.usage = this.validUsages[0];
    this.$emit(
      "wizardContinueButtonDisabled",
      this.wizardContinueButtonDisabled,
    );
  },
  methods: {
    disableUsage: function (usageValue) {
      return disableUsage({
        usageValue: usageValue,
        usage: this.usage,
        validUsages: this.validUsages,
      });
    },
  },
};
</script>

<style scoped>
.wizard-success-div label + label {
  margin-left: 0.5rem;
}
</style>
