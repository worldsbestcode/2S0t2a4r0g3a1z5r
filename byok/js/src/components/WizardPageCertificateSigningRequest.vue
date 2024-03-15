<template>
  <ul class="wizard-page-list">
    <li>
      <span>Country code <span class="hint">(2 letter code)</span></span>
      <input
        :value="countryCode"
        maxlength="2"
        class="input input-wide"
        @input="handleCountryCodeInput"
      />
    </li>
    <li>
      <span>State</span>
      <input v-model="state" maxlength="128" class="input input-wide" />
    </li>
    <li>
      <span>Locality</span>
      <input v-model="locality" maxlength="128" class="input input-wide" />
    </li>
    <li>
      <span>Organization</span>
      <input v-model="organization" maxlength="64" class="input input-wide" />
    </li>
    <li>
      <span>Organizational unit</span>
      <input
        v-model="organizationalUnit"
        maxlength="64"
        class="input input-wide"
      />
    </li>
    <li>
      <span>Common name</span>
      <input v-model="commonName" maxlength="64" class="input input-wide" />
    </li>
    <li>
      <span>Email</span>
      <input v-model="email" maxlength="255" class="input input-wide" />
    </li>
  </ul>
</template>

<script>
export default {
  title: "Certificate Signing Request",
  description:
    "Fill out the Distinguished Name for the Subject of the Certificate Signing Request. At least one field must be filled out",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      countryCode: {
        wizardSummaryText: "Country code",
        value: "",
      },
      state: {
        wizardSummaryText: "State",
        value: "",
      },
      locality: {
        wizardSummaryText: "Locality",
        value: "",
      },
      organization: {
        wizardSummaryText: "Organization",
        value: "",
      },
      organizationalUnit: {
        wizardSummaryText: "Organizational unit",
        value: "",
      },
      commonName: {
        wizardSummaryText: "Common name",
        value: "",
      },
      email: {
        wizardSummaryText: "Email",
        value: "",
      },
    };
  },
  computed: {
    wizardContinueButtonDisabled: function () {
      if (this.countryCode.length === 1) {
        return true;
      } else {
        return !(
          this.countryCode.length === 2 ||
          this.state.length > 0 ||
          this.locality.length > 0 ||
          this.organization.length > 0 ||
          this.organizationalUnit.length > 0 ||
          this.commonName.length > 0 ||
          this.email.length > 0
        );
      }
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
    handleCountryCodeInput: function (event) {
      let value = event.target.value;
      event.target.value = value.toUpperCase();
      this.countryCode = event.target.value;
    },
  },
};
</script>
