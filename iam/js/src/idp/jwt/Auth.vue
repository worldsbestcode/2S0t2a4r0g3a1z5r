<template>
  <ChcComboBox
    v-model="store.state.idp.jwtAuthType"
    label="Authentication type"
    :values="authTypes"
  />

  <!-- HMAC -->
  <ChcInput
    v-if="store.state.idp.jwtAuthType === 'HMAC'"
    v-model="store.state.idp.hmacKey"
    label="HMAC Key"
    placeholder="Key"
    hint="Base64 encoded"
  />

  <!-- PKI -->
  <br v-if="store.state.idp.jwtAuthType === 'PKI'" />
  <textarea
    v-if="store.state.idp.jwtAuthType === 'PKI'"
    v-model="store.state.idp.pkiVerifyCert"
    :placeholder="fakeCertData"
    rows="10"
  >
  </textarea>

  <!-- JWKS URL -->
  <ChcInput
    v-if="store.state.idp.jwtAuthType === 'URL'"
    v-model="store.state.idp.jwksUrl"
    label="JSON Web Key URL"
    placeholder="https://example.com/keys.json"
  />

  <!-- PKI -->
  <br v-if="store.state.idp.jwtAuthType === 'URL'" />
  <textarea
    v-if="store.state.idp.jwtAuthType === 'URL'"
    v-model="store.state.idp.jwksTlsCa"
    :placeholder="fakeCertData"
    rows="10"
  >
  </textarea>
</template>

<script setup>
import { ref } from "vue";
import { useStore } from "vuex";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcInput from "$shared/components/ChcInput.vue";

const authTypes = ref([
  { value: "HMAC", label: "HMAC" },
  { value: "PKI", label: "PKI Certificate" },
  { value: "URL", label: "JWKS URL" },
]);

const store = useStore();

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
