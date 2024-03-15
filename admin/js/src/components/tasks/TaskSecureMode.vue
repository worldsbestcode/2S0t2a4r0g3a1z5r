<template>
  <WizardPage
    title="Security Mode"
    description="Choose specialized modes of operation"
    :loading="getSecureModeSettingsLoading"
    style="margin-top: 2rem"
  >
    <ChcLabel div label="Information">
      <p>
        Changing your secure mode settings will clear all users, clear all keys,
        and restart the HSM.
      </p>
      <p style="margin-bottom: 0">
        Enabling a secure mode will force dual-control logins for several
        actions:
      </p>
      <ul>
        <li>HSM identity management</li>
        <li>password-protected PKI</li>
        <li>some forms of key entry</li>
        <li>misc actions</li>
      </ul>
      <p>PCI mode enables a mandatory session timeouts for HSM logins.</p>
    </ChcLabel>

    <ChcToggle
      v-model="defaultMode"
      side="left"
      label="Standard"
      class="space-label-toggle"
    />

    <ChcToggle
      v-model="state.fipsEnabled"
      side="left"
      label="FIPS"
      class="space-label-toggle"
    />

    <ChcToggle
      v-model="state.pciEnabled"
      side="left"
      label="PCI"
      class="space-label-toggle"
    />

    <ChcLabel v-if="requireConfirmation" div>
      <header class="secure-mode-warning__header">
        <img
          class="secure-mode-warning__icon"
          src="/shared/static/warning.svg"
        />
        All users and keys will be cleared. This operation cannot be undone.
      </header>
      <label class="secure-mode-warning__body">
        Type "confirm" to perform this action
        <input
          v-model="state.secureModeConfirm"
          class="chc-input secure-mode-warning__input"
        />
      </label>
    </ChcLabel>
  </WizardPage>

  <div v-if="waitingForHsm" class="waiting-for-hsm">
    <LoadingSpinner loading />

    <h1>Waiting for HSM</h1>
    <p style="color: var(--secondary-text-color)">
      You will be automatically sent to the login page once the HSM finishes
      rebooting.
    </p>
  </div>
  <!-- hide footer if waiting screen is active -->
  <TaskWizardPageFooter
    v-else
    :loading="updateSecureModeSettingsLoading"
    :disabled="disableContinue"
    @click="updateSecureModeSettings"
  />
</template>

<script setup>
import axios from "axios";
import { computed, reactive, ref } from "vue";
import { useToast } from "vue-toastification";
import { useStore } from "vuex";

import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";
import LoadingSpinner from "$shared/components/LoadingSpinner.vue";
import WizardPage from "$shared/components/wizard/WizardPage.vue";

import TaskWizardPageFooter from "@/components/TaskWizardPageFooter.vue";
import { useTaskFinish } from "@/composables";

const toast = useToast();
const store = useStore();
const taskFinish = useTaskFinish();

const getSecureModeSettingsLoading = ref(false);
const updateSecureModeSettingsLoading = ref(false);
const waitingForHsm = ref(false);

const state = reactive({
  fipsEnabled: false,
  pciEnabled: false,
  initialFipsEnabled: null,
  initialPciEnabled: null,

  secureModeConfirm: "",
});

const defaultMode = computed({
  get: () => !state.fipsEnabled && !state.pciEnabled,
  set: () => {
    state.fipsEnabled = false;
    state.pciEnabled = false;
  },
});

const requireConfirmation = computed(() => {
  return (
    !getSecureModeSettingsLoading.value &&
    (state.fipsEnabled !== state.initialFipsEnabled ||
      state.pciEnabled !== state.initialPciEnabled)
  );
});

const disableContinue = computed(
  () => requireConfirmation.value && state.secureModeConfirm !== "confirm",
);

function waitForHsm() {
  waitingForHsm.value = true;
  return new Promise((resolve) => {
    let hasReturnedFalseOnce = false;
    let clearLoginCheckInterval = setInterval(() => {
      axios.get("/admin/v1/isup").then((response) => {
        const isUp = response.data.isup;
        if (hasReturnedFalseOnce) {
          if (isUp) {
            clearInterval(clearLoginCheckInterval);
            resolve();
          }
        } else {
          if (!isUp) {
            hasReturnedFalseOnce = true;
          }
        }
      });
    }, 6000);
  });
}

function getSecureModeSettings() {
  axios
    .get("/kmes/v7/system/security/modes", {
      loading: getSecureModeSettingsLoading,
      errorContext: "Failed to fetch secure mode settings",
    })
    .then((response) => {
      // todo: Fails with data is undefined if we are not logged
      // kmes API does not follow new APIs...
      const data = response.data?.response ?? {};
      state.initialFipsEnabled = data.fips;
      state.initialPciEnabled = data.pci;

      state.fipsEnabled = data.fips;
      state.pciEnabled = data.pci;
    });
}

function removeSecureModeNotification() {
  return store.dispatch("notifications/deleteSetupNotification", "SecureMode");
}

function updateSecureModeSettings() {
  axios
    .put(
      "/kmes/v7/system/security/modes",
      {
        fips: state.fipsEnabled,
        pci: state.pciEnabled,
      },
      {
        loading: updateSecureModeSettingsLoading,
        errorContext: "Failed to update secure mode settings",
      },
    )
    .then(async (response) => {
      const hsmRebooting = response.data.response?.jobId;
      if (hsmRebooting) {
        toast("The HSM will now reboot.");
        toast("Secure mode settings updated");
        removeSecureModeNotification();

        await waitForHsm();
        await store.dispatch("auth/logout");

        window.location.href = "/";
        // login will automatically send user to next step.
      } else {
        toast("Secure mode settings updated");

        taskFinish("SecureMode");
      }
    });
}

getSecureModeSettings();
</script>

<style scoped>
.secure-mode-warning__header {
  background: var(--primary-color);
  color: var(--primary-background-color);
  font-weight: 700;
  font-size: 18px;

  display: flex;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  align-items: center;

  border-top-left-radius: 15px;
  border-top-right-radius: 15px;
}

.secure-mode-warning__icon {
  background: #efdbdb;
  padding: 0.5rem;
  border-radius: 15px;

  height: 50px;
  width: 50px;
}
.secure-mode-warning__body {
  background: var(--secondary-background-color);
  border: 1px solid var(--border-color);
  border-bottom-left-radius: 15px;
  border-bottom-right-radius: 15px;

  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
  padding: 0.75rem 1.5rem;

  font-weight: 500;
}

.secure-mode-warning__input {
  min-width: unset;
  width: 300px;
  height: 42px;
}

.waiting-for-hsm {
  flex-direction: column;
  display: flex;
  align-items: center;
  justify-content: center;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--primary-background-color);
  overflow: auto;
}

.space-label-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
