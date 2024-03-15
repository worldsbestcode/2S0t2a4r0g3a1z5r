<template>
  <ul class="wizard-page-list">
    <li>
      <span>Load key slot</span>
      <button class="button button-wide" @click="handleLoadKeySlotClick">
        Select
      </button>
    </li>
    <li>
      <span>Create key block</span>
      <button class="button button-wide" @click="handleCreateKeyBlockClick">
        Select
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  title: "Key Destination",
  description: "Select the destination for the key",
  defaultData: function () {
    return {
      isKeySlot: {
        value: null,
      },
    };
  },
  methods: {
    handleLoadKeySlotClick: function () {
      this.isKeySlot = true;
      this.nextPage();
    },
    handleCreateKeyBlockClick: function () {
      this.isKeySlot = false;
      this.nextPage();
    },
  },
};
</script>
