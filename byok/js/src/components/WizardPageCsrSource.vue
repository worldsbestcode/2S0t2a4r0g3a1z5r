<template>
  <ul class="wizard-page-list">
    <li>
      <span>Select key slot</span>
      <button class="button button-wide" @click="setIsKeySlot(true)">
        Select
      </button>
    </li>
    <li>
      <span>Input key block</span>
      <button class="button button-wide" @click="setIsKeySlot(false)">
        Select
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  title: "Key Slot or Key Block",
  description: "Select a key slot or input a key block",
  defaultData: function () {
    return {
      isKeySlot: {
        value: null,
      },
    };
  },
  methods: {
    setIsKeySlot: function (value) {
      this.isKeySlot = value;
      this.nextPage();
    },
  },
};
</script>
