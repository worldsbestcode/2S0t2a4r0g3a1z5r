<template>
  <wizard-base
    wizard-title="Load Diebold Number Table"
    wizard-summary-title="Diebold Number Table"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageDiebold from "@/components/WizardPageDiebold.vue";
import WizardPageChooseKeySlot from "@/components/WizardPageChooseKeySlot.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardLoadDieboldSuccess from "@/components/WizardLoadDieboldSuccess.vue";

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    return {
      wizardPages: [
        wizardPage({
          component: WizardPageChooseKeySlot,
          description: "Select a key slot for your Diebold number table",
          props: {
            hideSelectNext: true,
            keyType: this.isGpMode() ? "" : "diebold",
          },
        }),
        wizardPage({ component: WizardPageDiebold }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let keySlot = this.wizardPages[0].data.slot.value;
      let dieboldTable = this.wizardPages[1].data.dieboldTable.value.join("");

      let url = `/clusters/sessions/${this.getSessionId()}/keytable`;
      if (!this.isGpMode()) {
        url += `/diebold`;
      }
      url += `/${keySlot}`;
      let body = {
        key: {
          table: dieboldTable,
        },
      };

      this.$httpV2
        .post(url, body, { silenceToastError: true })
        .then((data) => {
          let successComponentWithData = {
            ...WizardLoadDieboldSuccess,
            data: function () {
              return {
                keyChecksum: data.key.kcv,
                slot: data.slot,
              };
            },
          };
          this.$emit("refreshTableInformation");
          success(
            "The Diebold number table has been loaded.",
            successComponentWithData,
          );
        })
        .catch((error) => {
          fail(`Failed to load Diebold number table: ${error.message}`);
        });
    },
  },
};
</script>
