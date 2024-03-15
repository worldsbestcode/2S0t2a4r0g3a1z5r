<template>
  <wizard-base
    wizard-title="Import Key"
    wizard-summary-title="Key block"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageLoadData from "@/components/WizardPageLoadData.vue";
import WizardPageEncryptingKey from "@/components/WizardPageEncryptingKey.vue";
import WizardPageChooseKeySlot from "@/components/WizardPageChooseKeySlot.vue";
import WizardPageSlotLabel from "@/components/WizardPageSlotLabel.vue";
import WizardPageMajorKey from "@/components/WizardPageMajorKey.vue";
import WizardPageKeyType from "@/components/WizardPageKeyType.vue";
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
        wizardPage({
          component: WizardPageEncryptingKey,
          props: {
            disableExistingKeySlotButton: () =>
              this.wizardPages[1].data.keyType.value === "Public",
          },
        }),
        wizardPage({
          component: WizardPageMajorKey,
          pageEnabled: () => this.wizardPages[2].data.isMajorKey.value === true,
        }),
        wizardPage({
          title: "Select a KEK",
          description: "Select a KEK to use",
          component: WizardPageChooseKeySlot,
          pageEnabled: () =>
            this.wizardPages[2].data.isMajorKey.value === false,
          data: function () {
            return {
              slot: {
                wizardSummaryText: "KEK slot number",
              },
            };
          },
          props: {
            selectKekMode: true,
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
          component: WizardPageChooseKeySlot,
          props: {
            keyType: () => {
              if (this.isGpMode()) {
                return "";
              } else {
                return this.wizardPages[1].data.keyType.value === "Symmetric"
                  ? "symmetric"
                  : "asymmetric";
              }
            },
          },
        }),
        wizardPage({ component: WizardPageSlotLabel }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let keyBlock = this.wizardPages[0].data.data.value;
      let keyType = this.wizardPages[1].data.keyType.value.toLowerCase();
      let keyModifier = this.wizardPages[1].data.symmetricKeyModifier.value;
      let isMajorKey = this.wizardPages[2].data.isMajorKey.value;
      let majorKeyType = this.wizardPages[3].data.majorKeyType.value;
      let kekSlot = this.wizardPages[4].data.slot.value;
      let keyBlockSlot = this.wizardPages[5].data.slot.value;
      let keyBlockLabel = this.wizardPages[6].data.label.value;

      let sessionUrl = `/clusters/sessions/${this.getSessionId()}`;

      if (!isMajorKey) {
        let translateUrl = `${sessionUrl}/keyblock/translate`;
        let translateBody = {
          key: {
            kekSlot: kekSlot,
          },
          outputFormat: {
            majorKey: "PMK",
          },
        };
        if (keyType === "private") {
          translateBody.key.privateKeyBlock = keyBlock;
        } else {
          translateBody.key.keyBlock = keyBlock;
          translateBody.outputFormat.modifier = keyModifier;
        }

        try {
          let data = await this.$httpV2.post(translateUrl, translateBody, {
            silenceToastError: true,
          });
          keyBlock = data.keyBlock;
          majorKeyType = "PMK";
        } catch (error) {
          fail(`Failed to translate key: ${error.message}`);
          return;
        }
      }

      let keyTableUrl = `${sessionUrl}/keytable`;
      if (!this.isGpMode()) {
        keyTableUrl += "/";
        if (keyType === "symmetric") {
          keyTableUrl += "symmetric";
        } else {
          keyTableUrl += "asymmetric";
        }
      }
      if (keyBlockSlot !== -1) {
        keyTableUrl += `/${keyBlockSlot}`;
      }
      let keyTableBody = {
        key: {
          majorKey: majorKeyType,
          label: keyBlockLabel,
        },
      };
      if (keyType === "symmetric") {
        keyTableBody.key.keyBlock = keyBlock;
        keyTableBody.key.modifier = keyModifier;
      } else {
        keyTableBody.key[`${keyType}KeyBlock`] = keyBlock;
      }

      try {
        let data = await this.$httpV2.post(keyTableUrl, keyTableBody, {
          silenceToastError: true,
        });
        let keyChecksum = data.key.tpkKcv || data.key.kcv;
        let clearPublicKeyBlock = data.key.clearPublicKeyBlock;
        let publicKeyBlock = data.key.publicKeyBlock;
        let slot = data.tpkSlot || data.slot;
        let successComponentWithData = {
          ...WizardImportKeyBlockSuccess,
          data: function () {
            return {
              keyChecksum: keyChecksum,
              slot: slot,
              clearPublicKeyBlock: clearPublicKeyBlock,
              publicKeyBlock: publicKeyBlock,
            };
          },
        };
        this.$emit("refreshTableInformation");
        success(`The key block has been imported.`, successComponentWithData);
      } catch (error) {
        fail(`Failed to import key: ${error.message}`);
      }
    },
  },
};
</script>
