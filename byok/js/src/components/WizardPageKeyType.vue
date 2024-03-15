<template>
  <ul class="wizard-page-list">
    <li>
      <span>Symmetric - key usage</span>
      <select v-model="symmetricKeyModifier" class="button button-wide">
        <option value="null">Select a key usage</option>
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
    <li class="wizard-page-symmetric-key-type">
      <button
        class="button button-wide"
        :disabled="symmetricKeyModifier === null"
        @click="handleSymmetricClick"
      >
        Select
      </button>
    </li>
    <li>
      <span>Private Key</span>
      <button class="button button-wide" @click="handlePrivateClick">
        Select
      </button>
    </li>
    <li v-if="!disableTpkOption">
      <span>Trusted Public Key</span>
      <button class="button button-wide" @click="handlePublicClick">
        Select
      </button>
    </li>
  </ul>
</template>

<script>
import { modifierAliases } from "@/utils/models.js";
import { toHexString } from "@/utils/misc.js";

export default {
  title: "Key Type",
  description: "Select the key type",
  defaultData: function () {
    return {
      keyType: {
        value: null,
        wizardSummaryText: "Key type",
      },
      symmetricKeyModifier: {
        value: null,
        wizardSummaryText: "Key usage",
      },
    };
  },
  props: {
    disableTpkOption: {
      type: Boolean,
      default: false,
    },
  },
  data: function () {
    return {
      modifierAliases,
    };
  },
  methods: {
    toHexString: toHexString,
    handleSymmetricClick: function () {
      this.keyType = "Symmetric";
      this.symmetricKeyModifier = parseInt(this.symmetricKeyModifier);
      this.nextPage();
    },
    handlePrivateClick: function () {
      this.keyType = "Private";
      this.symmetricKeyModifier = null;
      this.nextPage();
    },
    handlePublicClick: function () {
      this.keyType = "Public";
      this.symmetricKeyModifier = null;
      this.nextPage();
    },
  },
};
</script>

<style scoped>
.wizard-page-list > .wizard-page-symmetric-key-type {
  border-top: none;
  justify-content: flex-end;
}
</style>
