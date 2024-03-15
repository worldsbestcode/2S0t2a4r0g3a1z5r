<template>
  <ul class="wizard-page-list">
    <li>
      <span>MFK</span>
      <button
        :disabled="disableMfkOption() || !mfkLoaded"
        class="button button-wide"
        @click="handleMfkClick"
      >
        Select
      </button>
    </li>
    <li>
      <span>PMK</span>
      <button
        :disabled="!pmkLoaded"
        class="button button-wide"
        @click="handlePmkClick"
      >
        Select
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  inject: ["getSessionId"],
  title: "Major Key Type",
  description: "Select the major key type",
  defaultData: function () {
    return {
      majorKeyType: {
        value: null,
        wizardSummaryText: "Major key",
      },
    };
  },
  props: {
    disableMfkOption: {
      type: Function,
      default: () => false,
    },
  },
  data: function () {
    return {
      mfkLoaded: false,
      pmkLoaded: false,
    };
  },
  mounted: async function () {
    let url = `/clusters/sessions/${this.getSessionId()}/major-keys`;
    let data = await this.$httpV2.get(url, {
      errorContextMessage: "Failed to get major key status",
    });
    let majorKeys = data.majorKeys;
    let pmk = majorKeys.find((x) => x.name === "PMK");
    let mfk = majorKeys.find((x) => x.name === "MFK");
    this.pmkLoaded = pmk.loaded;
    this.mfkLoaded = mfk.loaded;
  },
  methods: {
    handleMfkClick: function () {
      this.majorKeyType = "MFK";
      this.nextPage();
    },
    handlePmkClick: function () {
      this.majorKeyType = "PMK";
      this.nextPage();
    },
  },
};
</script>
