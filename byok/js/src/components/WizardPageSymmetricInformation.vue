<template>
  <ul class="wizard-page-list">
    <li>
      <span>Symmetric - algorithm</span>
      <select v-model="algorithm" class="button button-wide">
        <option :value="null">Select a key algorithm</option>
        <option v-for="type in symmetricTypes" :key="type" :value="type">
          {{ type }}
        </option>
      </select>
    </li>
    <li v-if="!hideModifier">
      <span>Symmetric - key usage</span>
      <select v-model="modifier" class="button button-wide">
        <option :value="null">Select a key usage</option>
        <option
          v-for="(alias, modifier) in modifierAliases"
          :key="modifier"
          :value="modifier"
        >
          {{ alias }}
          ({{ toHexString(modifier) }})
        </option>
      </select>
    </li>
  </ul>
</template>

<script>
import { modifierAliases, symmetricTypes } from "@/utils/models.js";
import { toHexString } from "@/utils/misc.js";

export default {
  title: "Key Information",
  description: "Provide information for the symmetric key",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      algorithm: {
        value: null,
        wizardSummaryText: "Algorithm",
      },
      modifier: {
        value: null,
        wizardSummaryText: "Key usage",
      },
    };
  },
  props: {
    hideModifier: {
      type: Boolean,
      default: false,
    },
  },
  data: function () {
    return {
      symmetricTypes: symmetricTypes,
      modifierAliases,
    };
  },
  computed: {
    wizardContinueButtonDisabled: function () {
      if (this.hideModifier) {
        return this.algorithm === null;
      }

      return this.algorithm === null || this.modifier === null;
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
  methods: {
    toHexString: toHexString,
  },
};
</script>
