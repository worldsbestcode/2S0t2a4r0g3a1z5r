<template>
  <wizard-base
    wizard-title="Load PKCS8 Private Key"
    wizard-summary-title="PKCS8 Private Key"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageLoadData from "@/components/WizardPageLoadData.vue";
import WizardPagePassword from "@/components/WizardPagePassword.vue";
import WizardPageMajorKey from "@/components/WizardPageMajorKey.vue";
import WizardPageUsages from "@/components/WizardPageUsages.vue";
import WizardPageChooseKeySlot from "@/components/WizardPageChooseKeySlot.vue";
import WizardPageSlotLabel from "@/components/WizardPageSlotLabel.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardImportKeyBlockSuccess from "@/components/WizardImportKeyBlockSuccess.vue";

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    return {
      wizardPages: [
        wizardPage({
          component: WizardPageLoadData,
          title: "Input PKCS8 Private Key",
          description: "Import the PKCS8 private key",
          data: function () {
            return {
              data: {
                wizardSummaryText: "PKCS8 private key",
              },
            };
          },
        }),
        wizardPage({ component: WizardPagePassword }),
        wizardPage({ component: WizardPageMajorKey }),
        wizardPage({
          component: WizardPageUsages,
          title: "Key Usage",
          description: "Select the key usage",
          props: {
            keyType: "ECC",
          },
        }),
        wizardPage({
          component: WizardPageChooseKeySlot,
          description: "Select a key slot for your PKCS8 private key",
          props: {
            keyType: this.isGpMode() ? "" : "asymmetric",
          },
        }),
        wizardPage({ component: WizardPageSlotLabel }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let pkcs8 = this.wizardPages[0].data.data.value;
      let password = this.wizardPages[1].data.password.value;
      if (password !== "") {
        password = btoa(password);
      }
      let majorKeyType = this.wizardPages[2].data.majorKeyType.value;
      let usage = this.wizardPages[3].data.usage.value;
      let securityUsage = this.wizardPages[3].data.securityUsage.value;
      let slot = this.wizardPages[4].data.slot.value;
      let label = this.wizardPages[5].data.label.value;

      if (usage.length === 0) {
        usage = null;
      }

      let url = `/clusters/sessions/${this.getSessionId()}/keytable`;
      if (!this.isGpMode()) {
        url += "/asymmetric";
      }
      if (slot !== -1) {
        url += `/${slot}`;
      }
      let body = {
        key: {
          pkcs8: pkcs8,
          password: password,
          usage: usage,
          securityUsage: securityUsage,
          majorKey: majorKeyType,
          label: label,
        },
      };
      this.$httpV2
        .post(url, body, { silenceToastError: true })
        .then((data) => {
          let successComponentWithData = {
            ...WizardImportKeyBlockSuccess,
            data: function () {
              return {
                keyChecksum: data.key.kcv,
                slot: data.slot,
                clearPublicKeyBlock: data.key.clearPublicKeyBlock,
                publicKeyBlock: data.key.publicKeyBlock,
              };
            },
          };
          this.$emit("refreshTableInformation");
          success(
            "The PKCS8 private key has been loaded.",
            successComponentWithData,
          );
        })
        .catch((error) => {
          fail(`Failed to load the PKCS8 private key: ${error.message}`);
        });
    },
  },
};
</script>
