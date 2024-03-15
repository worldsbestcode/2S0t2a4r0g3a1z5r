<template>
  <ul class="wizard-page-list">
    <li>
      <span>Challenge password <span class="hint">(optional)</span></span>
      <input
        v-model="challengePassword"
        class="input input-wide"
        type="password"
      />
    </li>
    <li>
      <span>Subject alternate name <span class="hint">(optional)</span></span>
      <input v-model="subjectAlternateName" class="input input-wide" />
    </li>
    <li class="pki-key-usage-header">
      PKI key usage <span class="hint">(optional)</span>
    </li>
    <li
      v-for="(value, key) in pkiUsageTypes"
      :key="value"
      class="pki-key-usage"
    >
      <label>{{ value }}</label>
      <input v-model="pkiKeyUsage" type="checkbox" :value="key" />
    </li>
  </ul>
</template>

<script>
export default {
  title: "Certificate Signing Request Details",
  description: "Fill out the Certificate Signing Request Details",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      challengePassword: {
        value: "",
      },
      subjectAlternateName: {
        wizardSummaryText: "Subject alternate name",
        value: "",
      },
      pkiKeyUsage: {
        wizardSummaryText: "PKI key usage",
        value: [],
      },
    };
  },
  data: function () {
    return {
      pkiUsageTypes: {
        critical: "Critical",
        digitalSignature: "Digital signature",
        nonRepudiation: "Non repudiation",
        keyEncipherment: "Key encipherment",
        dataEncipherment: "Data encipherment",
        keyAgreement: "Key agreement",
        keyCertSign: "Certificate sign",
        cRLSign: "CRL sign",
        encipherOnly: "Encipher only",
        decipherOnly: "Decipher only",
      },
    };
  },
  mounted: function () {
    this.$emit("wizardContinueButtonDisabled", false);
  },
};
</script>

<style scoped>
ul li.pki-key-usage {
  border-top: 0;
}

ul li.pki-key-usage-header {
  display: block;
  text-align: center;
}
</style>
