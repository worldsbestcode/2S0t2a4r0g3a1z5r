<template>
  <wizard-base
    wizard-title="Generate Key Pair"
    wizard-summary-title="Key Pair"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageNewKeyType from "@/components/WizardPageNewKeyType.vue";

import WizardRandomKey from "@/components/WizardRandomKey.vue";

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    let generateKeyPairPages = WizardRandomKey.data.bind(this)().wizardPages;
    let keyTypeIndex = generateKeyPairPages.findIndex(
      (x) => x.name === "keyType",
    );
    generateKeyPairPages[keyTypeIndex] = wizardPage({
      name: "keyType",
      component: WizardPageNewKeyType,
      props: {
        disableSymmetricOption: true,
      },
    });

    return {
      wizardPages: generateKeyPairPages,
    };
  },
  methods: {
    wizardSubmit: WizardRandomKey.methods.wizardSubmit,
  },
};
</script>
