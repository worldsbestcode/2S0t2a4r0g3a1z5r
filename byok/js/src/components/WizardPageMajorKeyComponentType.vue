<template>
  <ul class="wizard-page-list">
    <li>
      <span>3TDES</span>
      <button class="button button-wide" @click="setComponentType('3TDES')">
        Select
      </button>
    </li>
    <li>
      <span>AES-256</span>
      <button class="button button-wide" @click="setComponentType('AES-256')">
        Select
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  title: "Major Key Component Type",
  description: "Select the major key component type",
  defaultData: function () {
    return {
      componentType: {
        value: null,
        wizardSummaryText: "Major key component type",
      },
    };
  },
  methods: {
    setComponentType: function (componentType) {
      this.componentType = componentType;
      this.nextPage();
    },
  },
};
</script>
