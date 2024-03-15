<template>
  <div class="wizard-bread-container">
    <div class="wizard-bread-image-container">
      <img class="wizard-bread-image" />
    </div>

    <ChcWizardBreadCrumbs v-bind="$attrs" />
  </div>
</template>

<script setup>
import { inject } from "vue";

import ChcWizardBreadCrumbs from "@/wizard/ChcWizardBreadCrumbs.vue";
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
