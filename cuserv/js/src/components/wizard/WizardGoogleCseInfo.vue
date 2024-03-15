<template>
  <WizardPage title="Service Info" :loading="loading">
    <ChcLabel div label="Identity Provider Type">
      <div class="radio-container">
        <ChcRadio
          v-for="idp in idpTypes"
          :key="idp"
          v-model="idpType"
          :value="idp"
          type="radio"
          :label="idp"
        />
      </div>
    </ChcLabel>

    <ChcSelect
      v-if="idpType === 'Existing'"
      v-model="authMechanismUuid"
      label="Auth Mechanism - IdP"
    >
      <option
        v-for="authMechanism in state.authMechanisms"
        :key="authMechanism.uuid"
        :value="authMechanism.uuid"
      >
        {{ authMechanism.name }} - {{ authMechanism.idpName }}
      </option>
    </ChcSelect>

    <ChcToggle
      v-model="defaultWhitelisted"
      label="New Users Enabled By Default"
    />

    <ChcInput
      v-if="idpType === 'OpenID Connect'"
      v-model="oidcUrl"
      label="OpenID Connect URL"
      placeholder="URL"
    />

    <ChcLabel v-if="idpType === 'OpenID Connect'" label="OpenID Connect PKI" />
    <div
      v-if="idpType === 'OpenID Connect'"
      style="display: grid; padding-bottom: 2rem"
    >
      <textarea v-model="oidcTlsCa" :placeholder="fakeCertData" rows="10">
      </textarea>
    </div>

    <ChcInput
      v-model="rotationPeriod"
      label="Rotation Period for Personal Keys"
      placeholder="Rotation period"
    />

    <ChcInput
      v-model="emailSuffix"
      label="Email Suffix"
      hint="e.g. futurex.com"
      placeholder="Email suffix"
    />
  </WizardPage>
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, defineProps, reactive, ref } from "vue";

import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcRadio from "$shared/components/ChcRadio.vue";
import ChcSelect from "$shared/components/ChcSelect.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";
import WizardPage from "$shared/components/wizard/WizardPage.vue";

const emit = defineEmits([
  "update:serviceGoogleCseIdpType",
  "update:serviceGoogleCseAuthMechUuid",
  "update:serviceGoogleCseOidcUrl",
  "update:serviceGoogleCseOidcTlsCa",
  "update:serviceGoogleCseRotationPeriod",
  "update:serviceGoogleCseEmailSuffix",
  "update:serviceGoogleCseDefaultWhitelisted",
]);

const idpTypes = [
  "Existing",
  "OpenID Connect",
  "VirtuCrypt VIP",
  "VirtuCrypt Test",
];

const props = defineProps({
  serviceGoogleCseIdpType: {
    type: String,
    required: true,
  },
  serviceGoogleCseAuthMechUuid: {
    type: String,
    default: undefined,
  },
  serviceGoogleCseOidcUrl: {
    type: String,
    default: undefined,
  },
  serviceGoogleCseOidcTlsCa: {
    type: String,
    default: undefined,
  },
  serviceGoogleCseRotationPeriod: {
    type: String,
    default: undefined,
  },
  serviceGoogleCseEmailSuffix: {
    type: String,
    required: true,
  },
  serviceGoogleCseDefaultWhitelisted: {
    type: Boolean,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  authMechanisms: [],
});

const idpType = computed({
  get() {
    return props.serviceGoogleCseIdpType;
  },
  set(value) {
    emit("update:serviceGoogleCseIdpType", value);
  },
});
const authMechanismUuid = computed({
  get() {
    return props.serviceGoogleCseAuthMechUuid;
  },
  set(value) {
    emit("update:serviceGoogleCseAuthMechUuid", value);
  },
});
const oidcUrl = computed({
  get() {
    return props.serviceGoogleCseOidcUrl;
  },
  set(value) {
    emit("update:serviceGoogleCseOidcUrl", value);
  },
});
const oidcTlsCa = computed({
  get() {
    return props.serviceGoogleCseOidcTlsCa;
  },
  set(value) {
    emit("update:serviceGoogleCseOidcTlsCa", value);
  },
});
const rotationPeriod = computed({
  get() {
    return props.serviceGoogleCseRotationPeriod;
  },
  set(value) {
    emit("update:serviceGoogleCseRotationPeriod", value);
  },
});
const emailSuffix = computed({
  get() {
    return props.serviceGoogleCseEmailSuffix;
  },
  set(value) {
    emit("update:serviceGoogleCseEmailSuffix", value);
  },
});
const defaultWhitelisted = computed({
  get() {
    return props.defaultWhitelisted;
  },
  set(value) {
    emit("update:serviceGoogleCseDefaultWhitelisted", value);
  },
});

axios
  .get("/cuserv/v1/users/authmechs", {
    params: {
      page: 1,
      pageSize: 100,
    },
    errorContext: "Failed to fetch authentication mechanisms",
    loading,
  })
  .then((response) => {
    state.authMechanisms = response.data.results.filter(
      (x) => x.authType === "Jwt",
    );
  });

const fakeCertData = `Paste certificate data here

-----BEGIN CERTIFICATE-----
MIIC9DCCAlWgAwIBAgIHBQDEAAAAfjAKBggqhkjOPQQDBDCBiDELMAkGA1UEBhMC
VVMxCzAJBgNVBAgMAlRYMREwDwYDVQQHDAhCdWx2ZXJkZTEQMA4GA1UECgwHRnV0
dXJleDEjMCEGA1UEAwwaRnV0dXJleCBUZXN0IFJvb3QgQ0EgKEVDQykxIjAgBgkq
hkiG9w0BCQEWE3N1cHBvcnRAZnV0dXJleC5jb20wIBcNMDAwMTAxMDAwMDAwWhgP
MjEwMDEyMzEwMDAwMDBaMIGIMQswCQYDVQQGEwJVUzELMAkGA1UECAwCVFgxETAP
BgNVBAcMCEJ1bHZlcmRlMRAwDgYDVQQKDAdGdXR1cmV4MSMwIQYDVQQDDBpGdXR1
cmV4IFRlc3QgUm9vdCBDQSAoRUNDKTEiMCAGCSqGSIb3DQEJARYTc3VwcG9ydEBm
dXR1cmV4LmNvbTCBmzAQBgcqhkjOPQIBBgUrgQQAIwOBhgAEATtzCpz0566rQZkT
tMbjA61jC43WqqoEGU5nKNeseIqG/ml+zpRZn7hoYBQs4GRJ+jKWU+wymhDk/NjI
V4tFtvVxAD2mdPL8Qg9qliMu4NjiKYjYA2UsQ86tLvPpY2wxr57rReO/arbjxttI
HNAMYUElqc6sUbVF9M2FDqQHiRNRbWsoo2MwYTAfBgNVHSMEGDAWgBSQ5G8Fs1Iq
X1dgDla2ECXSO8BjzzAdBgNVHQ4EFgQUkORvBbNSKl9XYA5WthAl0jvAY88wDwYD
VR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMCAgQwCgYIKoZIzj0EAwQDgYwAMIGI
AkIBdrKkVN8Js4Vaw5MINvGBAKENKIbpDBI6fePz7GXn+tlmKafPZZbyaHv4Ufq1
+3V+jQXEvWsORA1qH98kaX7ygNoCQgFc4hy3VW8Ap9LR2ArQTUiJj101Iuc7Mnaa
7S0UsbCILNuBiJ6uMujNdY2Cq8w70XLxLbw+9uVyM6SoVacZD3WV9w==
-----END CERTIFICATE-----
`;
</script>
