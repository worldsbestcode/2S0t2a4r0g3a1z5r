<template>
  <div>
    <ul class="wizard-page-list cipher-ul">
      <li>
        <span>Padding</span>
        <select v-model="padding" class="button button-wide">
          <option v-for="padding in paddings" :key="padding" :value="padding">
            {{ padding }}
          </option>
        </select>
      </li>
      <li v-if="type() === 'CBC'" class="form-switch">
        <span>Clear IV</span>
        <input v-model="clearIv" class="form-check-input" type="checkbox" />
      </li>
      <li v-if="type() === 'CBC'">
        <span>IV</span>
        <input v-model="iv" class="input button-wide" />
      </li>
    </ul>
  </div>
</template>

<script>
let paddings = ["None", "PKCS #7", "Bit", "Zero"];

export default {
  title: "Cipher",
  description: "Fill out the cipher details",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      padding: {
        value: "None",
        wizardSummaryText: "Padding",
      },
      clearIv: {
        value: null,
      },
      iv: {
        value: null,
        wizardSummaryText: "IV",
      },
    };
  },
  props: {
    type: {
      type: Function,
      required: true,
    },
  },
  data: function () {
    return {
      paddings,
    };
  },
  computed: {
    wizardContinueButtonDisabled: function () {
      return false;
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

<style scoped>
.cipher-ul {
  margin-top: 1rem;
}

.form-check-input {
  --height: 1.4rem;
  height: var(--height);
  width: calc(var(--height) * 2);
}
</style>
