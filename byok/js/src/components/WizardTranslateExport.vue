<template>
  <wizard-base
    wizard-title="Translate Key"
    wizard-summary-title="Key"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import WizardBase from "@/components/WizardBase.vue";
import WizardTranslateKey from "@/components/WizardTranslateKey.vue";

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  props: {
    keyBlock: {
      type: String,
      required: true,
    },
    keyType: {
      type: String,
      required: true,
    },
    keyModifier: {
      type: Number,
      required: false,
    },
    majorKey: {
      type: String,
      required: true,
    },
    symmetricType: {
      type: String,
      required: false,
    },
  },
  data: function () {
    let pages = WizardTranslateKey.data.bind(this)().wizardPages;

    function override(pageName, override) {
      let pageIndex = pages.findIndex((x) => x.name === pageName);
      pages[pageIndex] = {
        ...pages[pageIndex],
        ...override,
      };
    }

    override("keyBlock", {
      pageEnabled: () => false,
      data: {
        data: {
          value: this.keyBlock,
        },
      },
    });

    override("keyType", {
      pageEnabled: () => false,
      data: {
        keyType: {
          value: this.keyType,
        },
      },
    });

    override("symmetricInformation", {
      pageEnabled: () => false,
      data: {
        algorithm: {
          value: this.symmetricType,
        },
        modifier: {
          value: this.keyModifier,
        },
      },
    });

    override("encryptingKeyTypeIsMajorKey", {
      pageEnabled: () => false,
      data: {
        isMajorKey: {
          value: true,
        },
      },
    });

    override("encryptingMajorKey", {
      pageEnabled: () => false,
      data: {
        majorKeyType: {
          value: this.majorKey,
        },
      },
    });

    return {
      wizardPages: pages,
    };
  },
  methods: {
    wizardSubmit: WizardTranslateKey.methods.wizardSubmit,
  },
};
</script>
