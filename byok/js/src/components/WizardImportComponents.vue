<template>
  <wizard-base
    wizard-title="Import XOR Components"
    wizard-summary-title="XOR Component"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageSymmetricInformation from "@/components/WizardPageSymmetricInformation.vue";
import WizardPageMajorKey from "@/components/WizardPageMajorKey.vue";
import WizardPageUsages from "@/components/WizardPageUsages.vue";
import WizardPageKeyDestination from "@/components/WizardPageKeyDestination.vue";
import WizardPageChooseKeySlot from "@/components/WizardPageChooseKeySlot.vue";
import WizardPageSlotLabel from "@/components/WizardPageSlotLabel.vue";
import WizardPageLoadComponent from "@/components/WizardPageLoadComponent.vue";
import WizardPageNumberOfComponents from "@/components/WizardPageNumberOfComponents.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardRandomKeySuccess from "@/components/WizardRandomKeySuccess.vue";

import { canMFKWrap } from "@/utils/misc.js";

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    return {
      wizardPages: [
        wizardPage({
          component: WizardPageSymmetricInformation,
        }),
        wizardPage({
          component: WizardPageMajorKey,
          props: {
            disableMfkOption: () =>
              !canMFKWrap({
                keyType: "Symmetric",
                ...this.wizardPages[0].data,
              }),
          },
        }),
        wizardPage({
          component: WizardPageUsages,
          props: {
            keyType: "DES",
            keyModifier: () => this.wizardPages[0].data.modifier.value,
          },
        }),
        wizardPage({ component: WizardPageKeyDestination }),
        wizardPage({
          component: WizardPageChooseKeySlot,
          pageEnabled: () => this.wizardPages[3].data.isKeySlot.value,
          props: {
            keyType: () => {
              if (this.isGpMode()) {
                return "";
              } else {
                return "symmetric";
              }
            },
          },
        }),
        wizardPage({
          component: WizardPageSlotLabel,
          pageEnabled: () => this.wizardPages[3].data.isKeySlot.value,
        }),
        wizardPage({
          component: WizardPageNumberOfComponents,
        }),
        wizardPage({
          component: WizardPageLoadComponent,
          props: {
            majorKey: () => this.wizardPages[1].data.majorKeyType.value,
            majorKeyLoad: false,
            componentType: () => this.wizardPages[0].data.algorithm.value,
            numberOfComponents: () =>
              this.wizardPages[6].data.numberOfComponents.value,
          },
        }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let modifier = this.wizardPages[0].data.modifier.value;
      let type = this.wizardPages[0].data.algorithm.value;
      let majorKey = this.wizardPages[1].data.majorKeyType.value;
      let usage = this.wizardPages[2].data.usage.value;
      let securityUsage = this.wizardPages[2].data.securityUsage.value;
      let isKeySlot = this.wizardPages[3].data.isKeySlot.value;
      let slot = this.wizardPages[4].data.slot.value;
      let label = this.wizardPages[5].data.label.value;
      let numberOfComponents =
        this.wizardPages[6].data.numberOfComponents.value;
      let wrappedComponents = this.wizardPages[7].data.wrappedComponents.value;

      if (usage.length === 0) {
        usage = null;
      }

      let sessionUrl = `/clusters/sessions/${this.getSessionId()}`;

      let authReceiptUrl = `${sessionUrl}/keyload/auth-receipt`;
      let authReceiptBody = {
        majorKey: majorKey,
        numComponents: numberOfComponents,
        usage: usage,
        securityUsage: securityUsage,
        type: type,
        modifier: modifier,
      };

      let authReceipts = [];
      let partKcvs = [];
      for (let wrappedComponent of wrappedComponents) {
        authReceiptBody.input = wrappedComponent;
        let data = await this.$httpV2.post(authReceiptUrl, authReceiptBody, {
          errorContextMessage: "Failed to convert component to auth receipt",
        });
        authReceipts.push(data.authReceipt);
        partKcvs.push(data.partKcv);
      }

      let importUrl;
      if (isKeySlot) {
        importUrl = `${sessionUrl}/keytable`;
        if (!this.isGpMode()) {
          importUrl += "/symmetric";
        }
        if (slot !== -1) {
          importUrl += `/${slot}`;
        }
      } else {
        importUrl = `${sessionUrl}/keyblock`;
      }
      let importBody = {
        key: {
          authReceipts: authReceipts,
        },
      };
      if (isKeySlot) {
        importBody.key.label = label;
        importBody.key.majorKey = majorKey;
      }

      try {
        let data = await this.$httpV2.post(importUrl, importBody, {
          silenceToastError: true,
        });
        let successComponentWithData = {
          ...WizardRandomKeySuccess,
          data: function () {
            return {
              partKcvs: partKcvs,
              slot: data.slot,
              kcv: data.key.kcv,
              tpkSlot: data.tpkSlot,
              tpkKcv: data.key.tpkKcv,
              keyBlock: data.key.keyBlock,
              clearPublicKeyBlock: data.key.clearPublicKeyBlock,
              publicKeyBlock: data.key.publicKeyBlock,
              privateKeyBlock: data.key.privateKeyBlock,
            };
          },
        };
        this.$emit("refreshTableInformation");
        success(`The components have been imported.`, successComponentWithData);
      } catch (error) {
        fail(`Failed to import components: ${error.message}`);
      }
    },
  },
};
</script>
