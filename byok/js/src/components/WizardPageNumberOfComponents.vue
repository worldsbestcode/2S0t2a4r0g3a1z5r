<template>
  <ul class="wizard-page-list">
    <li>
      <span>Number of components <span class="hint">(2 - 12)</span></span>
      <input
        v-model.number="numberOfComponents"
        class="input input-wide number-of-components"
        type="number"
        min="2"
        max="12"
        step="1"
      />
    </li>
  </ul>
</template>

<script>
export default {
  title: "Number of components",
  description: "Enter the number of components",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      numberOfComponents: {
        wizardSummaryText: "Number of components",
        value: 2,
      },
    };
  },
  computed: {
    wizardContinueButtonDisabled: function () {
      let numberOfComponents = parseInt(this.numberOfComponents);
      return (
        isNaN(numberOfComponents) ||
        this.numberOfComponents < 2 ||
        this.numberOfComponents > 12
      );
    },
  },
  watch: {
    wizardContinueButtonDisabled: function (newValue) {
      this.$emit("wizardContinueButtonDisabled", newValue);
    },
  },
  mounted: function () {
    this.$emit("wizardContinueButtonDisabled", false);
  },
};
</script>

<style></style>
