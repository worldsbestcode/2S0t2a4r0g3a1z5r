<template>
  <wizard-base
    wizard-title="Random Key"
    wizard-summary-title="Random Key"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage, wizardData } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageKeyDestination from "@/components/WizardPageKeyDestination.vue";
import WizardPageNewKeyType from "@/components/WizardPageNewKeyType.vue";
import WizardPageSymmetricInformation from "@/components/WizardPageSymmetricInformation.vue";
import WizardPageRsaInformation from "@/components/WizardPageRsaInformation.vue";
import WizardPageEccInformation from "@/components/WizardPageEccInformation.vue";
import WizardPageEncryptingKey from "@/components/WizardPageEncryptingKey.vue";
import WizardPageCipher from "@/components/WizardPageCipher.vue";
import WizardPageKeyBlockHeader from "@/components/WizardPageKeyBlockHeader.vue";
import WizardPageMajorKey from "@/components/WizardPageMajorKey.vue";
import WizardPageUsages from "@/components/WizardPageUsages.vue";
import WizardPageChooseKeySlot from "@/components/WizardPageChooseKeySlot.vue";
import WizardPageSlotLabel from "@/components/WizardPageSlotLabel.vue";

import WizardPageOutputFormat from "@/components/WizardPageOutputFormat.vue";

import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardRandomKeySuccess from "@/components/WizardRandomKeySuccess.vue";

import { newCanMFKWrap } from "@/utils/misc.js";

import { randomKey, translateKey } from "@/guardian.js";

import { getValidUsages } from "@/utils/models.js";

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    const data = () => {
      return wizardData(this.wizardPages);
    };
    return {
      wizardPages: [
        wizardPage({
          name: "keyType",
          component: WizardPageNewKeyType,
        }),
        wizardPage({
          name: "symmetricInformation",
          component: WizardPageSymmetricInformation,
          pageEnabled: () => data().keyType.keyType === "Symmetric",
        }),
        wizardPage({
          name: "rsaInformation",
          component: WizardPageRsaInformation,
          pageEnabled: () => data().keyType.keyType === "RSA",
        }),
        wizardPage({
          name: "eccInformation",
          component: WizardPageEccInformation,
          pageEnabled: () => data().keyType.keyType === "ECC",
        }),

        wizardPage({
          name: "encryptingKey",
          description: "Select how the key will be encrypted",
          component: WizardPageEncryptingKey,
        }),
        wizardPage({
          name: "encryptingMajorKey",
          component: WizardPageMajorKey,
          props: {
            disableMfkOption: () =>
              !newCanMFKWrap({
                ...data().keyType,
                ...data().symmetricInformation,
                ...data().rsaInformation,
                ...data().eccInformation,
              }),
          },
          pageEnabled: () => data().encryptingKey.isMajorKey,
        }),
        wizardPage({
          name: "encryptingKeySlot",
          title: "Select the Encrypting Key Slot",
          component: WizardPageChooseKeySlot,
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
          pageEnabled: () => !data().encryptingKey.isMajorKey,
        }),

        // If !data().encryptingKey.isMajorKey, assume key block is the destination
        wizardPage({
          name: "keyDestination",
          component: WizardPageKeyDestination,
          pageEnabled: () => data().encryptingKey.isMajorKey,
        }),
        wizardPage({
          name: "destinationKeySlot",
          title: "Select the Destination Key Slot",
          component: WizardPageChooseKeySlot,
          props: {
            keyType: () => {
              if (this.isGpMode()) {
                return "";
              } else {
                return data().keyType.keyType === "Symmetric"
                  ? "symmetric"
                  : "asymmetric";
              }
            },
          },
          pageEnabled: () => data().keyDestination.isKeySlot,
        }),
        wizardPage({
          name: "destinationKeySlotLabel",
          component: WizardPageSlotLabel,
          pageEnabled: () => data().keyDestination.isKeySlot,
        }),

        wizardPage({
          name: "outputFormat",
          title: "Key Format",
          description: "Select the key's format",
          component: WizardPageOutputFormat,
          pageEnabled: () => !data().keyDestination.isKeySlot,
          props: {
            hideRawEncryptionFormats: () => data().encryptingKey.isMajorKey,
            keyIsSymmetric: () => data().keyType.keyType === "Symmetric",

            wrappingKeyType: () => {
              let isMajorKey = data().encryptingKey.isMajorKey;
              let majorKey = data().encryptingMajorKey.majorKeyType;
              let kekInformation = data().encryptingKeySlot.keyInformation;

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
          name: "usages",
          component: WizardPageUsages,
          props: {
            keyType: () => {
              if (data().keyType.keyType === "Symmetric") {
                return "DES";
              } else {
                return "ECC";
              }
            },
            keyModifier: () => data().symmetricInformation.modifier,
          },
          pageEnabled: () =>
            data().keyDestination.isKeySlot ||
            ["Futurex", "Cryptogram"].includes(
              data().outputFormat.outputFormat,
            ),
        }),
        wizardPage({
          name: "keyBlockHeader",
          component: WizardPageKeyBlockHeader,
          props: {
            formatType: () => data().outputFormat.outputFormat,

            wrappingKeyType: () => {
              let isMajorKey = data().encryptingKey.isMajorKey;
              let majorKey = data().encryptingMajorKey.majorKeyType;
              let keySlotInformation = data().encryptingKeySlot.keyInformation;

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

            keyInitialUsage: () => data().usages.usage,

            keyType: () => {
              if (data().keyType.keyType === "Symmetric") {
                return data().symmetricInformation.algorithm;
              } else {
                return data().keyType.keyType;
              }
            },

            keyTypeForGetValidUsages: () => {
              if (data().keyType.keyType === "Symmetric") {
                return "DES";
              } else {
                return "ECC";
              }
            },

            keyModifier: () => data().symmetricInformation.modifier,
          },
          pageEnabled: () =>
            ["TR-31", "International", "AKB"].includes(
              data().outputFormat.outputFormat,
            ),
        }),
        wizardPage({
          name: "cipher",
          component: WizardPageCipher,
          props: {
            type: () => data().outputFormat.outputFormat,
          },
          pageEnabled: () =>
            ["ECB", "CBC"].includes(data().outputFormat.outputFormat),
        }),

        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let data = wizardData(this.wizardPages);

      let keyType = data.keyType.keyType;
      let { algorithm, modifier } = data.symmetricInformation;
      let { modulus, exponent } = data.rsaInformation;
      let curve = data.eccInformation.curve;

      let isMajorKey = data.encryptingKey.isMajorKey;
      let majorKey = data.encryptingMajorKey.majorKeyType;
      let encryptingKeySlot = data.encryptingKeySlot.slot;
      let encryptingKeyType = data.encryptingKeySlot?.keyInformation?.type;

      let isKeySlot = data.keyDestination.isKeySlot;
      let slot = data.destinationKeySlot.slot;
      let label = data.destinationKeySlotLabel.label;

      let outputFormat = data.outputFormat.outputFormat;
      let { usage, securityUsage } = data.usages;
      let keyBlockHeader = data.keyBlockHeader.keyBlockHeader;
      let { padding, clearIv, iv } = data.cipher;

      const validUsages = getValidUsages({
        type: keyType === "Symmetric" ? "DES" : "ECC",
        gpMode: this.isGpMode(),
        modifier: modifier,
      });

      async function translate(options) {
        let temporaryKeyMajorKey;
        if (options.newWrappingKeyIsMajorKey) {
          temporaryKeyMajorKey = options.newWrappingMajorKey;
        } else {
          if (encryptingKeyType.includes("DES")) {
            temporaryKeyMajorKey = "MFK";
          } else {
            temporaryKeyMajorKey = "PMK";
          }
        }

        const temporaryKey = await randomKey({
          keyType,
          majorKey: temporaryKeyMajorKey,

          usage: validUsages[0],
          securityUsage,
          algorithm,
          modifier,
          modulus,
          exponent,
          curve,
        });
        const keyBlockKey =
          keyType === "Symmetric" ? "keyBlock" : "privateKeyBlock";
        const kekWrappedKey = await translateKey({
          keyType,
          keyModifier: modifier,
          keyAlgorithm: algorithm,

          wrappedByMajorKey: true,
          wrappingMajorKey: temporaryKeyMajorKey,

          newKeyBlockHeader: keyBlockHeader,
          newUsage: usage,
          newSecurityUsage: securityUsage,
          newOutputFormat: outputFormat,
          newIv: iv,
          newClearIv: clearIv,
          newPadding: padding,
          ...options,
          keyBlock: temporaryKey.key[keyBlockKey],
        });
        temporaryKey.key[keyBlockKey] = kekWrappedKey.keyBlock;
        return temporaryKey;
      }

      let result;
      try {
        if (isMajorKey) {
          if (
            isKeySlot ||
            ["Cryptogram", "Futurex"].includes(
              outputFormat,
            ) /* key block, no translation */
          ) {
            result = await randomKey({
              loadingToKeySlot: isKeySlot,
              keyType,
              keySlot: slot,
              label,
              majorKey,
              usage,
              securityUsage,
              algorithm,
              modifier,
              modulus,
              exponent,
              curve,
            });
          } else {
            // Key block
            result = await translate({
              newWrappingKeyIsMajorKey: true,
              newWrappingMajorKey: majorKey,
            });
          }
        } else {
          // KEK wrapped
          result = await translate({
            newWrappingKeyIsMajorKey: false,
            newWrappingKekKeySlot: encryptingKeySlot,
          });
        }

        let successComponentWithData = {
          ...WizardRandomKeySuccess,
          data: function () {
            return {
              slot: result.slot,
              kcv: result.key.kcv,
              tpkSlot: result.tpkSlot,
              tpkKcv: result.key.tpkKcv,
              keyBlock: result.key.keyBlock,
              clearPublicKeyBlock: result.key.clearPublicKeyBlock,
              publicKeyBlock: result.key.publicKeyBlock,
              privateKeyBlock: result.key.privateKeyBlock,
            };
          },
        };
        this.$emit("refreshTableInformation");
        success(`The random key has been generated.`, successComponentWithData);
      } catch (error) {
        fail(`Failed to generate random key: ${error.message}`);
      }
    },
  },
};
</script>
