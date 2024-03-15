<template>
  <wizard-base
    wizard-title="Translate Key"
    wizard-summary-title="Key"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage, wizardData } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageLoadData from "@/components/WizardPageLoadData.vue";
import WizardPageNewKeyType from "@/components/WizardPageNewKeyType.vue";
import WizardPageEncryptingKey from "@/components/WizardPageEncryptingKey.vue";
import WizardPageMajorKey from "@/components/WizardPageMajorKey.vue";
import WizardPageChooseKeySlot from "@/components/WizardPageChooseKeySlot.vue";
import WizardPageKeyBlockHeader from "@/components/WizardPageKeyBlockHeader.vue";
import WizardPageUsages from "@/components/WizardPageUsages.vue";
import WizardPageOutputFormat from "@/components/WizardPageOutputFormat.vue";
import WizardPageCipher from "@/components/WizardPageCipher.vue";
import WizardPageSymmetricInformation from "@/components/WizardPageSymmetricInformation.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardTranslateKeySuccess from "@/components/WizardTranslateKeySuccess.vue";
import { translateKey } from "@/guardian.js";

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    return {
      wizardPages: [
        wizardPage({
          name: "keyBlock",
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
        wizardPage({
          name: "keyType",
          component: WizardPageNewKeyType,
        }),
        wizardPage({
          name: "symmetricInformation",
          component: WizardPageSymmetricInformation,
          pageEnabled: () => {
            let isSymmetric =
              wizardData(this.wizardPages).keyType.keyType === "Symmetric";
            return isSymmetric;
          },
        }),
        wizardPage({
          name: "encryptingKeyTypeIsMajorKey",
          component: WizardPageEncryptingKey,
        }),
        wizardPage({
          name: "encryptingMajorKey",
          title: "Encrypting Major Key Type",
          description: "Select the encrypting major key type",
          component: WizardPageMajorKey,
          pageEnabled: () =>
            wizardData(this.wizardPages).encryptingKeyTypeIsMajorKey.isMajorKey,
          data: function () {
            return {
              majorKeyType: {
                wizardSummaryText: "Encrypting major key",
              },
            };
          },
        }),
        wizardPage({
          name: "encryptingSlot",
          title: "Encrypting KEK Slot Number",
          description: "Select the encrypting KEK slot number",
          component: WizardPageChooseKeySlot,
          pageEnabled: () =>
            !wizardData(this.wizardPages).encryptingKeyTypeIsMajorKey
              .isMajorKey,
          data: function () {
            return {
              slot: {
                wizardSummaryText: "Encrypting KEK slot number",
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
          name: "outputFormat",
          title: "Key Format",
          description: "Select the key's format",
          component: WizardPageOutputFormat,
          pageEnabled: () =>
            !wizardData(this.wizardPages).encryptingKeyTypeIsMajorKey
              .isMajorKey,
          props: {
            wrappingKeyType: () => {
              let data = wizardData(this.wizardPages);
              let isMajorKey = data.encryptingKeyTypeIsMajorKey.isMajorKey;
              let majorKey = data.encryptingMajorKey.majorKeyType;
              let kekInformation = data.encryptingSlot.keyInformation;

              if (isMajorKey) {
                if (majorKey === "PMK") {
                  return "AES-256";
                } else {
                  return "3TDES";
                }
              } else {
                return kekInformation.type;
              }
            },
          },
        }),
        wizardPage({
          name: "cipher",
          component: WizardPageCipher,
          props: {
            type: () => {
              return wizardData(this.wizardPages).outputFormat.outputFormat;
            },
          },
          pageEnabled: () => {
            let outputFormat = wizardData(this.wizardPages).outputFormat
              .outputFormat;
            return ["ECB", "CBC"].includes(outputFormat);
          },
        }),
        wizardPage({
          name: "newEncryptingKeyTypeIsMajorKey",
          title: "New Encrypting Key",
          description: "Select the new encrypting key",
          component: WizardPageEncryptingKey,
          props: {
            disableExistingKeySlotButton: () =>
              !wizardData(this.wizardPages).encryptingKeyTypeIsMajorKey
                .isMajorKey,
          },
        }),
        wizardPage({
          name: "newEncryptingMajorKey",
          title: "New Encrypting Major Key Type",
          description: "Select the new encrypting major key type",
          component: WizardPageMajorKey,
          pageEnabled: () =>
            wizardData(this.wizardPages).newEncryptingKeyTypeIsMajorKey
              .isMajorKey,
          data: function () {
            return {
              majorKeyType: {
                wizardSummaryText: "New encrypting major key",
              },
            };
          },
          props: {
            disableMfkOption: () =>
              wizardData(this.wizardPages).encryptingMajorKey.majorKeyType ===
              "PMK",
          },
        }),
        wizardPage({
          name: "newEncryptingSlot",
          title: "New Encrypting KEK Slot Number",
          description: "Select the new encrypting KEK slot number",
          component: WizardPageChooseKeySlot,
          pageEnabled: () =>
            !wizardData(this.wizardPages).newEncryptingKeyTypeIsMajorKey
              .isMajorKey,
          data: function () {
            return {
              slot: {
                wizardSummaryText: "New encrypting KEK slot number",
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
          name: "newUsages",
          component: WizardPageUsages,
          props: {
            keyType: () => {
              if (
                wizardData(this.wizardPages).keyType.keyType === "Symmetric"
              ) {
                return "DES";
              } else {
                return "ECC";
              }
            },
            keyModifier: () =>
              wizardData(this.wizardPages).symmetricInformation.modifier,
          },
        }),
        wizardPage({
          name: "newOutputFormat",
          title: "New Output Format",
          component: WizardPageOutputFormat,
          description: "Select the new output format",
          data: function () {
            return {
              outputFormat: {
                wizardSummaryText: "New output format",
              },
            };
          },
          props: {
            hideRawEncryptionFormats: () =>
              wizardData(this.wizardPages).newEncryptingKeyTypeIsMajorKey
                .isMajorKey,
            keyIsSymmetric: () =>
              wizardData(this.wizardPages).keyType.keyType === "Symmetric",

            wrappingKeyType: () => {
              let data = wizardData(this.wizardPages);
              let isMajorKey = data.newEncryptingKeyTypeIsMajorKey.isMajorKey;
              let majorKey = data.newEncryptingMajorKey.majorKeyType;
              let kekInformation = data.newEncryptingSlot.keyInformation;

              if (isMajorKey) {
                if (majorKey === "PMK") {
                  return "AES-256";
                } else {
                  return "3TDES";
                }
              } else {
                return kekInformation.type;
              }
            },
          },
        }),
        wizardPage({
          name: "newKeyBlockHeader",
          component: WizardPageKeyBlockHeader,
          title: "New Key Block Header",
          description: "Select the new key block header",
          props: {
            formatType: () =>
              wizardData(this.wizardPages).newOutputFormat.outputFormat,

            wrappingKeyType: () => {
              let data = wizardData(this.wizardPages);
              let isMajorKey = data.newEncryptingKeyTypeIsMajorKey.isMajorKey;
              let majorKey = data.newEncryptingMajorKey.majorKeyType;
              let keySlotInformation = data.newEncryptingSlot.keyInformation;

              if (isMajorKey) {
                if (majorKey === "MFK") {
                  return "3TDES";
                } else {
                  return "AES-256";
                }
              } else {
                return keySlotInformation.type;
              }
            },

            keyInitialUsage: () => {
              return wizardData(this.wizardPages).newUsages.usage;
            },

            keyType: () => {
              let data = wizardData(this.wizardPages);

              if (data.keyType.keyType === "Symmetric") {
                return data.symmetricInformation.algorithm;
              } else {
                return data.keyType.keyType;
              }
            },

            keyTypeForGetValidUsages: () => {
              if (
                wizardData(this.wizardPages).keyType.keyType === "Symmetric"
              ) {
                return "DES";
              } else {
                return "ECC";
              }
            },

            keyModifier: () => {
              let data = wizardData(this.wizardPages);
              return data.symmetricInformation.modifier;
            },
          },
          data: function () {
            return {
              keyBlockHeader: {
                wizardSummaryText: "New key block header",
              },
            };
          },
          pageEnabled: () => {
            let newOutputFormat = wizardData(this.wizardPages).newOutputFormat
              .outputFormat;
            return ["TR-31", "International", "AKB"].includes(newOutputFormat);
          },
        }),
        wizardPage({
          name: "newCipher",
          component: WizardPageCipher,
          title: "New Cipher",
          description: "Fill out the new cipher details",
          data: function () {
            return {
              padding: {
                wizardSummaryText: "New padding",
              },
              iv: {
                wizardSummaryText: "New IV",
              },
            };
          },
          props: {
            type: () => {
              return wizardData(this.wizardPages).newOutputFormat.outputFormat;
            },
          },
          pageEnabled: () => {
            let newOutputFormat = wizardData(this.wizardPages).newOutputFormat
              .outputFormat;
            return ["ECB", "CBC"].includes(newOutputFormat);
          },
        }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let data = wizardData(this.wizardPages);

      let keyBlock = data.keyBlock.data;
      let keyType = data.keyType.keyType;
      let keyModifier = data.symmetricInformation.modifier;
      let keyAlgorithm = data.symmetricInformation.algorithm;
      let encryptingKeyTypeIsMajorKey =
        data.encryptingKeyTypeIsMajorKey.isMajorKey;
      let encryptingMajorKey = data.encryptingMajorKey.majorKeyType;
      let encryptingSlot = data.encryptingSlot.slot;
      let outputFormat = data.outputFormat.outputFormat;
      let { padding, clearIv, iv } = data.cipher;
      let newEncryptingKeyTypeIsMajorKey =
        data.newEncryptingKeyTypeIsMajorKey.isMajorKey;
      let newEncryptingMajorKey = data.newEncryptingMajorKey.majorKeyType;
      let newEncryptingSlot = data.newEncryptingSlot.slot;
      let newKeyBlockHeader = data.newKeyBlockHeader.keyBlockHeader;
      let newUsage = data.newUsages.usage;
      let newSecurityUsage = data.newUsages.securityUsage;
      let newOutputFormat = data.newOutputFormat.outputFormat;
      let {
        padding: newPadding,
        clearIv: newClearIv,
        iv: newIv,
      } = data.newCipher;

      translateKey({
        keyBlock,
        keyType,
        keyModifier,
        keyAlgorithm,
        outputFormat,
        iv,
        clearIv,
        padding,

        wrappedByMajorKey: encryptingKeyTypeIsMajorKey,
        wrappingMajorKey: encryptingMajorKey,
        wrappingKekKeySlot: encryptingSlot,

        newWrappingKeyIsMajorKey: newEncryptingKeyTypeIsMajorKey,
        newWrappingMajorKey: newEncryptingMajorKey,
        newWrappingKekKeySlot: newEncryptingSlot,

        newKeyBlockHeader,
        newUsage,
        newSecurityUsage,
        newOutputFormat,
        newIv,
        newClearIv,
        newPadding,
      })
        .then((data) => {
          let successComponentWithData = {
            ...WizardTranslateKeySuccess,
            data: function () {
              return {
                keyChecksum: data.kcv,
                keyBlock: data.keyBlock,
              };
            },
          };
          success(`The key has been translated.`, successComponentWithData);
        })
        .catch((error) => {
          fail(`Failed to translate key: ${error.message}`);
        });
    },
  },
};
</script>
