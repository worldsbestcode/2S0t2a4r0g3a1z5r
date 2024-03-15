<template>
  <wizard-base
    wizard-title="Verify Key"
    wizard-summary-title="Key Block"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageLoadData from "@/components/WizardPageLoadData.vue";
import WizardPageMajorKey from "@/components/WizardPageMajorKey.vue";
import WizardPageKeyType from "@/components/WizardPageKeyType.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardVerifyKeySuccess from "@/components/WizardVerifyKeySuccess.vue";

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId"],
  data: function () {
    return {
      wizardPages: [
        wizardPage({
          component: WizardPageLoadData,
          title: "Input Key Block",
          description: "Import the key block or cryptogram value",
          data: function () {
            return {
              data: {
                wizardSummaryText: "Key block ",
              },
            };
          },
        }),
        wizardPage({ component: WizardPageKeyType }),
        wizardPage({ component: WizardPageMajorKey }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let keyBlock = this.wizardPages[0].data.data.value;
      let keyType = this.wizardPages[1].data.keyType.value.toLowerCase();
      let modifier = this.wizardPages[1].data.symmetricKeyModifier.value;
      let majorKeyType = this.wizardPages[2].data.majorKeyType.value;

      let url = `/clusters/sessions/${this.getSessionId()}/keyblock/info`;
      let body = { key: {} };
      if (keyType === "public" || keyType === "private") {
        body.key[`${keyType}KeyBlock`] = keyBlock;
        body.key.majorKey = majorKeyType;
      } else if (keyType === "symmetric") {
        body.key = {
          keyBlock: keyBlock,
          modifier: modifier,
          majorKey: majorKeyType,
        };
      }
      this.$httpV2
        .post(url, body, { silenceToastError: true })
        .then((data) => {
          let successComponentWithData = {
            ...WizardVerifyKeySuccess,
            data: function () {
              return {
                keyChecksum: data.key.kcv,
                majorKey: data.key.majorKey,
                securityUsage: data.key.securityUsage,
                usage: data.key.usage,
                tr31: data.tr31,
              };
            },
          };
          success("The key is valid.", successComponentWithData);
        })
        .catch((error) => {
          fail(`The key is not valid: ${error.message}`);
        });
    },
  },
};
</script>
