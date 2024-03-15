<template>
  <ul class="wizard-page-list">
    <li>
      <span>{{ futurexOrCryptogramText }}</span>
      <button
        class="button button-wide"
        @click="setOutputFormat(futurexOrCryptogramText)"
      >
        Select
      </button>
    </li>
    <li>
      <span>TR-31</span>
      <button class="button button-wide" @click="setOutputFormat('TR-31')">
        Select
      </button>
    </li>
    <li v-if="keyIsSymmetric()">
      <span>International KB</span>
      <button
        class="button button-wide"
        @click="setOutputFormat('International')"
      >
        Select
      </button>
    </li>
    <li>
      <span>AKB</span>
      <button class="button button-wide" @click="setOutputFormat('AKB')">
        Select
      </button>
    </li>
    <li v-if="!hideRawEncryptionFormats()">
      <span>AES-KWP</span>
      <button class="button button-wide" @click="setOutputFormat('KWP')">
        Select
      </button>
    </li>
    <li v-if="!hideRawEncryptionFormats()">
      <span>ECB</span>
      <button class="button button-wide" @click="setOutputFormat('ECB')">
        Select
      </button>
    </li>
    <li v-if="!hideRawEncryptionFormats()">
      <span>CBC</span>
      <button class="button button-wide" @click="setOutputFormat('CBC')">
        Select
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  title: "Output Format",
  description: "Select the output format",
  defaultData: function () {
    return {
      outputFormat: {
        value: null,
        wizardSummaryText: "Output format",
      },
    };
  },
  props: {
    hideRawEncryptionFormats: {
      type: Function,
      default: () => false,
    },

    keyIsSymmetric: {
      type: Function,
      default: () => true,
    },

    wrappingKeyType: {
      type: Function,
      required: true,
    },
  },
  computed: {
    futurexOrCryptogramText: function () {
      if (this.wrappingKeyType().includes("AES")) {
        return "Futurex";
      } else {
        return "Cryptogram";
      }
    },
  },
  methods: {
    setOutputFormat: function (outputFormat) {
      this.outputFormat = outputFormat;
      this.nextPage();
    },
  },
};
</script>
