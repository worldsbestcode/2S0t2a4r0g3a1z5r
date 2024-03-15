<template>
  <wizard-base
    wizard-title="Import Fragments"
    wizard-summary-title="Smart Card Fragments"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageSymmetricInformation from "@/components/WizardPageSymmetricInformation.vue";
import WizardPageKeyDestination from "@/components/WizardPageKeyDestination.vue";
import WizardPageChooseKeySlot from "@/components/WizardPageChooseKeySlot.vue";
import WizardPageLoadFragments from "@/components/WizardPageLoadFragments.vue";
import WizardRandomKeySuccess from "@/components/WizardRandomKeySuccess.vue";
import WizardPageSlotLabel from "@/components/WizardPageSlotLabel.vue";
import WizardPageMajorKey from "@/components/WizardPageMajorKey.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";
import WizardPageUsages from "@/components/WizardPageUsages.vue";

export default {
  name: "WizardImportSmartCards",
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    return {
      wizardPages: [
        // 0 - isKeySlot
        wizardPage({ component: WizardPageKeyDestination }),
        // 1 - algorithm, modifier
        wizardPage({
          component: WizardPageSymmetricInformation,
          description: "Select type of combined key",
        }),
        // 2 - majorKey
        wizardPage({
          component: WizardPageMajorKey,
          description: "Select major key for the combined key",
        }),
        // 3 - usage, securityUsage
        wizardPage({
          component: WizardPageUsages,
          description: "Select usage for the combined key",
          props: {
            keyType: "DES",
            keyModifier: () => this.wizardPages[1].data.modifier.value,
          },
        }),
        // 4 - slot
        wizardPage({
          component: WizardPageChooseKeySlot,
          pageEnabled: () => this.wizardPages[0].data.isKeySlot.value,
          props: {
            hideSelectNext: true,
            keyType: () => {
              if (this.isGpMode()) {
                return "";
              } else {
                return "symmetric";
              }
            },
          },
        }),
        // 5 - label
        wizardPage({
          component: WizardPageSlotLabel,
          pageEnabled: () => this.wizardPages[0].data.isKeySlot.value,
        }),
        // 6 - fragments
        wizardPage({
          component: WizardPageLoadFragments,
          props: {
            keyDetails: this.getAuthReceiptDetails,
          },
        }),
        // 7 - submit
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    getAllPageData: function () {
      let data = {
        isKeySlot: 0,
        algorithm: 1,
        modifier: 1,
        majorKeyType: 2,
        usage: 3,
        securityUsage: 3,
        slot: 4,
        label: 5,
        authReceipts: 6,
      };
      data = Object.fromEntries(
        Object.entries(data).map(([name, page]) => [
          name,
          this.wizardPages[page].data[name].value,
        ]),
      );
      return data;
    },
    getAuthReceiptDetails: function () {
      let data = this.getAllPageData();
      let details = {
        type: data.algorithm,
        modifier: data.modifier,
        usage: data.usage,
        securityUsage: data.securityUsage,
        majorKey: data.majorKeyType,
      };
      return details;
    },
    wizardSubmit: async function (success, fail) {
      let data = this.getAllPageData();

      let sessionId = this.getSessionId();
      let recombineUri;

      if (data.usage.length === 0) {
        data.usage = null;
      }

      if (data.isKeySlot) {
        let table = this.isGpMode() ? "" : "/symmetric";
        recombineUri = `/clusters/sessions/${sessionId}/keytable${table}/${data.slot}`;
      } else {
        recombineUri = `/clusters/sessions/${sessionId}/keyblock`;
      }

      let recombineBody = {
        key: {
          authReceipts: data.authReceipts,
        },
      };

      try {
        let result = await this.$httpV2.post(recombineUri, recombineBody, {
          silenceToastError: true,
        });
        let successComponentWithData = {
          ...WizardRandomKeySuccess,
          data: function () {
            return {
              ...WizardRandomKeySuccess.data(),
              slot: result.slot,
              kcv: result.key.kcv,
              keyBlock: result.key.keyBlock,
            };
          },
        };
        success("The key has been recombined", successComponentWithData);
      } catch (error) {
        fail(`Failed to recombine key: ${error.message}`);
      }
    },
  },
};
</script>
