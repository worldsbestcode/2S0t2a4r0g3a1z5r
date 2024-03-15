<template>
  <ul class="wizard-page-list">
    <li>
      <span>Major key</span>
      <button class="button button-wide" @click="handleMajorKeyClick">
        Select
      </button>
    </li>
    <li>
      <span>Existing key slot</span>
      <button
        :disabled="disableExistingKeySlotButton()"
        class="button button-wide"
        @click="handleExistingKeySlotClick"
      >
        Select
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  title: "Encrypting Key",
  description: "Select how the current key is encrypted",
  defaultData: function () {
    return {
      isMajorKey: {
        value: null,
      },
    };
  },
  props: {
    disableExistingKeySlotButton: {
      type: Function,
      default: function () {
        return false;
      },
    },
  },
  methods: {
    handleMajorKeyClick: function () {
      this.isMajorKey = true;
      this.nextPage();
    },
    handleExistingKeySlotClick: function () {
      this.isMajorKey = false;
      this.nextPage();
    },
  },
};
</script>
