<template>
  <wizard-base
    wizard-title="Load Major Key"
    wizard-summary-title="Major Key"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageNumberOfComponents from "@/components/WizardPageNumberOfComponents.vue";
import WizardPageLoadComponent from "@/components/WizardPageLoadComponent.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardLoadMajorKeyWithComponentsSuccess from "@/components/WizardLoadMajorKeyWithComponentsSuccess.vue";

function getComponentType(majorKey) {
  if (majorKey === "MFK" || majorKey === "KEK") {
    return "3TDES";
  } else {
    return "AES-256";
  }
}

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  props: {
    majorKey: {
      type: Object,
      required: true,
    },
  },
  data: function () {
    return {
      wizardPages: [
        wizardPage({
          pageEnabled: () => !this.majorKey.sessionInfo,
          component: WizardPageNumberOfComponents,
        }),
        wizardPage({
          component: WizardPageLoadComponent,
          props: {
            majorKey: () => this.majorKey.name,
            majorKeyLoad: true,
            componentType: getComponentType(this.majorKey.name),
          },
        }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let numberOfComponents =
        this.wizardPages[0].data.numberOfComponents.value;
      let wrappedComponent = this.wizardPages[1].data.wrappedComponent.value;

      if (this.majorKey.sessionInfo && this.majorKey.sessionInfo.want) {
        numberOfComponents = this.majorKey.sessionInfo.want;
      }

      if (!wrappedComponent) {
        fail(`Failed to load the component: failed to wrap component`);
        return;
      }

      let url = `/clusters/sessions/${this.getSessionId()}/major-keys/${
        this.majorKey.name
      }/partial-key-load`;
      let body = {
        type: getComponentType(this.majorKey.name),
        numComponents: numberOfComponents,
        input: wrappedComponent,
      };
      this.$httpV2
        .post(url, body, { silenceToastError: true })
        .then((data) => {
          let successComponentWithData = {
            ...WizardLoadMajorKeyWithComponentsSuccess,
            data: function () {
              return {
                have: data.have,
                want: data.want,
                partKcv: data.partKcv,
                kcv: data.kcv,
              };
            },
          };
          let successMessage = "The component has been loaded.";
          if (data.kcv) {
            successMessage = "The key has been loaded.";
          }
          success(successMessage, successComponentWithData);
        })
        .catch((error) => {
          fail(`Failed the load the component: ${error.message}`);
        })
        .finally(() => {
          this.$bus.emit("majorKeyPartialKeyLoad");
        });
    },
  },
};
</script>
