<template>
  <WizardPage
    title="Licensing"
    :loading="settingsLoading || licensesLoading"
    style="margin-top: 2rem"
  >
    <!-- Error -->
    <div v-if="!settingsLoading">
      <div class="error">
        {{ state.error }}
      </div>
      <br />
    </div>

    <!-- Serial -->
    <div v-if="!settingsLoading">Serial: {{ state.serial }}</div>

    <!-- Form -->
    <div v-if="!settingsLoading && !viewLicenses">
      <div>
        <ChcToggle v-model="state.onlineActivation" label="Online Activation" />
      </div>

      <div v-if="state.onlineActivation">
        <ChcInput v-model="state.productKey" label="Product Key" />
        <div
          v-for="(server, index) in state.activationServers"
          :key="index"
          class="row"
        >
          <ChcInput
            v-model="state.activationServers[index]"
            label="Activation Server"
          />
          <button value="-" @click="state.activationServers.splice(index, 1)">
            -
          </button>
        </div>
        <div class="row">
          <button @click="state.activationServers.push('')">+</button>
        </div>
      </div>

      <div v-if="!state.onlineActivation">
        License File:<br />
        <textarea
          v-model="state.licenseFile"
          placeholder="Paste license file here"
          rows="10"
          cols="60"
        >
        </textarea>
      </div>
    </div>

    <!-- Licenses -->
    <div v-if="!settingsLoading && viewLicenses">
      <div>Valid: {{ state.valid }}</div>
      <div>Warning: {{ state.warning }}</div>
      <div>Licensed State: {{ state.state }}</div>
      <div>HSM State: {{ state.hsmState }}</div>
      <div v-for="(lic, index) in state.licenses" :key="index">
        {{ lic.name }} = {{ lic.count }} ({{ lic.valid ? "Valid" : "Invalid" }})
      </div>
    </div>
  </WizardPage>
  <WizardPageFooter>
    <ChcButton secondary @click="skip">Skip</ChcButton>

    <ChcButton v-if="!viewLicenses" secondary @click.prevent="gotoLicenses"
      >View Licenses</ChcButton
    >
    <ChcButton v-if="!viewLicenses" @click.prevent="updateLicensing"
      >Save</ChcButton
    >

    <ChcButton v-if="viewLicenses" secondary @click.prevent="gotoForm"
      >Edit License</ChcButton
    >
    <ChcButton v-if="viewLicenses" @click.prevent="done">
      <span v-if="playlist">Continue</span>
      <span v-else>Finish</span>
    </ChcButton>
  </WizardPageFooter>
</template>

<script setup>
import axios from "axios";
import { inject, reactive, ref } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";
import WizardPage from "$shared/components/wizard/WizardPage.vue";
import WizardPageFooter from "$shared/components/wizard/WizardPageFooter.vue";

import { usePlaylist, useTaskFinish } from "@/composables";

const taskFinish = useTaskFinish();

const state = reactive({
  // Form
  onlineActivation: false,
  activationServers: [],
  productKey: "",
  licenseFile: "",
  error: null,
  serial: null,
  // Licenses
  warning: false,
  hsmState: null,
  valid: false,
  state: null,
  licenses: [], // graceExpiration, valid, splendaUuid, expiration, type, name, count
});

const playlist = usePlaylist();

const licensesLoading = ref(false);
const settingsLoading = ref(false);
const viewLicenses = ref(false);

function getLicensing() {
  axios
    .get("/luds/v1/licensing", {
      loading: settingsLoading,
      errorContext: "Failed to fetch licensing settings",
    })
    .then((response) => {
      const data = response.data;
      state.onlineActivation = data.onlineActivation;
      state.activationServers = data.activationServers;
      state.productKey = data.productKey;
      state.licenseFile = data.licenseFile;
      state.serial = data.serial;
      state.error = data.error;
    });
}

function updateLicensing() {
  axios
    .post(
      "/luds/v1/licensing",
      {
        onlineActivation: state.onlineActivation,
        activationServers: state.activationServers,
        productKey: state.productKey,
        licenseFile: state.licenseFile,
        force_update: true,
      },
      {
        loading: settingsLoading,
        errorContext: "Failed to update licensing settings",
      },
    )
    .then((response) => {
      state.error = response.error;
      getLicenses();
      viewLicenses.value = true;
    });
}

getLicensing();

function getLicenses() {
  licensesLoading.value = true;
  try {
    axios
      .get("/luds/v1/licenses", {
        errorContext: "Failed to fetch licenses",
      })
      .then((response) => {
        const data = response.data;
        state.warning = data.warning;
        state.state = data.state;
        state.hsmState = data.hsmState;
        state.valid = data.valid;
        state.licenses = data.licenses;
      });
  } catch {
    // Toast got it
  }
  licensesLoading.value = false;
}

const skip = inject("skip");

function gotoForm() {
  viewLicenses.value = false;
}

function gotoLicenses() {
  viewLicenses.value = true;
  getLicenses();
}

function done() {
  taskFinish("License");
}
</script>

<style scoped>
.error {
  color: red;
}
.row {
  padding: 10px;
}
</style>
