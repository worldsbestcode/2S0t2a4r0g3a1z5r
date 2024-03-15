<template>
  <div class="management-page">
    <header>
      <p>Certificates & Requests</p>
      <close-button @click="$emit('close')" />
    </header>

    <nav>
      <button class="button" @click="setWizard('WizardGenerateKeyPair')">
        Generate key pair
      </button>
      <button
        class="button"
        @click="setWizard('WizardGenerateTrustedPublicKey')"
      >
        Generate trusted public key
      </button>
      <button
        class="button"
        @click="setWizard('WizardGenerateCertificateSigningRequest')"
      >
        Generate certificate signing request
      </button>
      <button
        class="button"
        :disabled="!isGpMode()"
        @click="setWizard('WizardImportCertificate')"
      >
        Import certificate
      </button>
    </nav>

    <component :is="currentWizard" />
  </div>
</template>

<script>
import { wizardMixin, wizards } from "@/utils/wizard.js";
import CloseButton from "@/components/CloseButton.vue";
import WizardGenerateKeyPair from "@/components/WizardGenerateKeyPair.vue";
import WizardGenerateTrustedPublicKey from "@/components/WizardGenerateTrustedPublicKey.vue";
import WizardImportCertificate from "@/components/WizardImportCertificate.vue";
import WizardGenerateCertificateSigningRequest from "@/components/WizardGenerateCertificateSigningRequest.vue";

export default {
  components: {
    "close-button": CloseButton,
  },
  mixins: [wizardMixin],
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    return {
      wizards: wizards({
        WizardGenerateKeyPair,
        WizardGenerateTrustedPublicKey,
        WizardImportCertificate,
        WizardGenerateCertificateSigningRequest,
      }),
    };
  },
};
</script>

<style scoped>
nav {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  margin: 1rem;
  gap: 1rem;
}
</style>
