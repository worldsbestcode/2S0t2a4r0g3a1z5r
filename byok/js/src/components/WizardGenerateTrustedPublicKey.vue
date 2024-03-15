<template>
  <wizard-base
    wizard-title="Generate Trusted Public Key"
    wizard-summary-title="Trusted Public Key"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageLoadData from "@/components/WizardPageLoadData.vue";
import WizardPageMajorKey from "@/components/WizardPageMajorKey.vue";
import WizardPageUsages from "@/components/WizardPageUsages.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardGenerateTrustedPublicKeySuccess from "@/components/WizardGenerateTrustedPublicKeySuccess.vue";

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
          title: "Input Clear Public Key",
          description: "Import the clear public key",
          data: function () {
            return {
              data: {
                wizardSummaryText: "Clear public key",
              },
            };
          },
        }),
        wizardPage({ component: WizardPageMajorKey }),
        wizardPage({
          component: WizardPageUsages,
          title: "Key Usage",
          description: "Select the key usage",
          props: {
            keyType: "ECC (Public)",
            securityUsageHidden: true,
          },
        }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let clearPublicKeyBlock = this.wizardPages[0].data.data.value;
      let majorKey = this.wizardPages[1].data.majorKeyType.value;
      let securityUsage = this.wizardPages[2].data.securityUsage.value;
      let usage = this.wizardPages[2].data.usage.value;

      if (usage.length === 0) {
        usage = null;
      }

      let url = `/clusters/sessions/${this.getSessionId()}/pki/generate-tpk`;
      let body = {
        majorKey: majorKey,
        clearPublicKeyBlock: clearPublicKeyBlock,
        usage: usage,
        securityUsage: securityUsage,
      };
      this.$httpV2
        .post(url, body, { silenceToastError: true })
        .then((data) => {
          let successComponentWithData = {
            ...WizardGenerateTrustedPublicKeySuccess,
            data: function () {
              return {
                keyChecksum: data.kcv,
                publicKeyBlock: data.publicKeyBlock,
              };
            },
          };
          success(
            "The trusted public key has been generated.",
            successComponentWithData,
          );
        })
        .catch((error) => {
          fail(`Failed to generate trusted public key: ${error.message}`);
        });
    },
  },
};
</script>
