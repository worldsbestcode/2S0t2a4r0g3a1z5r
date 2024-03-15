<template>
  <wizard-base
    wizard-title="Import Certificate"
    wizard-summary-title="Certificate"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageLoadData from "@/components/WizardPageLoadData.vue";
import WizardPageChooseKeySlot from "@/components/WizardPageChooseKeySlot.vue";
import WizardPageSlotLabel from "@/components/WizardPageSlotLabel.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardImportCertificateSuccess from "@/components/WizardImportCertificateSuccess.vue";

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
          title: "Input Certificate",
          description: "Import the certificate",
          data: function () {
            return {
              data: {
                wizardSummaryText: "Certificate",
              },
            };
          },
        }),
        wizardPage({ component: WizardPageChooseKeySlot }),
        wizardPage({ component: WizardPageSlotLabel }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let certificate = this.wizardPages[0].data.data.value;
      let keySlot = this.wizardPages[1].data.slot.value;
      let label = this.wizardPages[2].data.label.value;

      let url = `/clusters/sessions/${this.getSessionId()}/keytable`;
      if (keySlot !== -1) {
        url += `/${keySlot}`;
      }
      let body = {
        key: {
          certificate: certificate,
          label: label,
        },
      };
      this.$httpV2
        .post(url, body, { silenceToastError: true })
        .then((data) => {
          let successComponentWithData = {
            ...WizardImportCertificateSuccess,
            data: function () {
              return {
                keyChecksum: data.key.kcv,
                slot: data.slot,
              };
            },
          };
          success(
            "The certificate has been imported.",
            successComponentWithData,
          );
        })
        .catch((error) => {
          fail(`Failed to import your certificate: ${error.message}`);
        });
    },
  },
};
</script>
