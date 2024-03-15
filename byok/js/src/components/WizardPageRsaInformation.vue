<template>
  <ul class="wizard-page-list">
    <li>
      <span
        >RSA - key size
        <span class="hint">(512 - 4096, divisible by 8)</span></span
      >
      <input
        type="number"
        step="8"
        min="512"
        max="4096"
        class="input button-wide modulus"
        :value="modulus"
        @input="handleModulusInput"
      />
    </li>
    <li>
      <span>RSA - exponent</span>
      <select v-model="exponent" class="button button-wide">
        <option :value="3">3</option>
        <option :value="5">5</option>
        <option :value="17">17</option>
        <option :value="257">257</option>
        <option :value="65537">65537</option>
      </select>
    </li>
  </ul>
</template>

<script>
export default {
  title: "Key Information",
  description: "Provide information for the RSA key",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      modulus: {
        value: 2048,
        wizardSummaryText: "Key size",
      },
      exponent: {
        value: 65537,
        wizardSummaryText: "Exponent",
      },
    };
  },
  computed: {
    wizardContinueButtonDisabled: function () {
      let validModulus =
        this.modulus >= 512 && this.modulus <= 4096 && this.modulus % 8 === 0;
      return !validModulus || this.exponent === null;
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
    handleModulusInput: function (event) {
      let value = Number(event.target.value);
      event.target.value = value;
      this.modulus = value;
    },
  },
};
</script>

<style scoped>
/* Remove arrows from type="number" */
.modulus {
  appearance: textfield;
}
.modulus::-webkit-outer-spin-button,
.modulus::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
