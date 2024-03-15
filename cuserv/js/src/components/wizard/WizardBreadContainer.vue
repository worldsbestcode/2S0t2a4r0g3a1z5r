<template>
  <div style="margin: 2rem; display: flex; justify-content: center">
    <div class="wizard-bread-container">
      <div class="wizard-bread-image-container">
        <img
          class="wizard-bread-image"
          :src="templateData?.params?.details?.icon"
        />
      </div>
      <div class="wizard-bread-name" :title="templateData?.objInfo?.name">
        {{ templateData?.objInfo?.name }}
      </div>

      <WizardBreadCrumbs v-bind="$attrs" />
    </div>
  </div>
</template>

<script setup>
import { inject } from "vue";

import WizardBreadCrumbs from "@/components/wizard/WizardBreadCrumbs.vue";

const templateData = inject("templateData");
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
