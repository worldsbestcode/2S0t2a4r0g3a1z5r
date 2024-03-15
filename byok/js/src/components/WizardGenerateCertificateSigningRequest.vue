<template>
  <wizard-base
    wizard-title="Generate Signing Request"
    wizard-summary-title="Signing Request"
    :wizard-pages="wizardPages"
    :wizard-submit="wizardSubmit"
  />
</template>

<script>
import { wizardPage } from "@/utils/wizard.js";
import WizardBase from "@/components/WizardBase.vue";

import WizardPageCsrSource from "@/components/WizardPageCsrSource.vue";
import WizardPageLoadData from "@/components/WizardPageLoadData.vue";
import WizardPageMajorKey from "@/components/WizardPageMajorKey.vue";
import WizardPageChooseKeySlot from "@/components/WizardPageChooseKeySlot.vue";
import WizardPageCertificateSigningRequest from "@/components/WizardPageCertificateSigningRequest.vue";
import WizardPageCertificateSigningRequestExtras from "@/components/WizardPageCertificateSigningRequestExtras.vue";
import WizardPageSubmit from "@/components/WizardPageSubmit.vue";

import WizardGenerateCertificateSigningRequestSuccess from "@/components/WizardGenerateCertificateSigningRequestSuccess.vue";

function getValues(data) {
  let values = {};
  for (let x in data) {
    if (data[x].value.length === 0) {
      values[x] = null;
    } else {
      values[x] = data[x].value;
    }
  }
  return values;
}

export default {
  components: {
    "wizard-base": WizardBase,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    return {
      wizardPages: [
        wizardPage({ component: WizardPageCsrSource }),
        wizardPage({
          component: WizardPageChooseKeySlot,
          props: {
            selectPrivateMode: true,
            keyType: this.isGpMode() ? "" : "asymmetric",
          },
          pageEnabled: () => this.wizardPages[0].data.isKeySlot.value,
        }),
        wizardPage({
          component: WizardPageLoadData,
          title: "Input Private Key Block",
          description: "Enter the private key block",
          data: function () {
            return {
              data: {
                wizardSummaryText: "Private key block",
              },
            };
          },
          pageEnabled: () => !this.wizardPages[0].data.isKeySlot.value,
        }),
        wizardPage({
          component: WizardPageMajorKey,
          pageEnabled: () => !this.wizardPages[0].data.isKeySlot.value,
        }),
        wizardPage({ component: WizardPageCertificateSigningRequest }),
        wizardPage({ component: WizardPageCertificateSigningRequestExtras }),
        wizardPage({ component: WizardPageSubmit }),
      ],
    };
  },
  methods: {
    wizardSubmit: async function (success, fail) {
      let isKeySlot = this.wizardPages[0].data.isKeySlot.value;
      let keySlot = this.wizardPages[1].data.slot.value;
      let keyBlock = this.wizardPages[2].data.data.value;
      let majorKey = this.wizardPages[3].data.majorKeyType.value;
      let {
        countryCode,
        state,
        locality,
        organization,
        organizationalUnit,
        commonName,
        email,
      } = getValues(this.wizardPages[4].data);
      let { challengePassword, subjectAlternateName, pkiKeyUsage } = getValues(
        this.wizardPages[5].data,
      );
      if (challengePassword) {
        challengePassword = btoa(challengePassword);
      }

      let asymmetricPath = this.isGpMode() ? "" : "asymmetric/";
      let url = `/clusters/sessions/${this.getSessionId()}`;

      let body = {
        pkiOptions: {
          subject: {
            commonName: commonName,
            email: email,
            stateOrProvinceName: state,
            country: countryCode,
            organization: organization,
            organizationalUnit: organizationalUnit,
            locality: locality,
          },
          san: subjectAlternateName,
          keyUsage: pkiKeyUsage,
        },
        password: challengePassword,
      };

      if (isKeySlot) {
        url += `/keytable/${asymmetricPath}${keySlot}/generate-csr`;
      } else {
        url += "/pki/generate-csr";
        body.majorKey = majorKey;
        body.privateKeyBlock = keyBlock;
      }

      this.$httpV2
        .post(url, body, { silenceToastError: true })
        .then((data) => {
          let successComponentWithData = {
            ...WizardGenerateCertificateSigningRequestSuccess,
            data: function () {
              return {
                csr: data.csr,
                fileName: `csr-${keySlot}.pem`,
              };
            },
          };
          success(
            "The certificate signing request has been generated.",
            successComponentWithData,
          );
        })
        .catch((error) => {
          fail(
            `Failed to generate a certificate signing request: ${error.message}`,
          );
        });
    },
  },
};
</script>
