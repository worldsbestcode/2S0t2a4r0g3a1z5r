<template>
  <ul class="wizard-page-list">
    <li v-if="!disableSymmetricOption">
      <span>Symmetric</span>
      <button class="button button-wide" @click="setKeyType('Symmetric')">
        Select
      </button>
    </li>
    <li>
      <span>RSA</span>
      <button class="button button-wide" @click="setKeyType('RSA')">
        Select
      </button>
    </li>
    <li>
      <span>ECC</span>
      <button class="button button-wide" @click="setKeyType('ECC')">
        Select
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  title: "Key Type",
  description: "Select the key type",
  defaultData: function () {
    return {
      keyType: {
        value: null,
        wizardSummaryText: "Key type",
      },
    };
  },
  props: {
    disableSymmetricOption: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    setKeyType: function (type) {
      this.keyType = type;
      this.nextPage();
    },
  },
};
</script>
