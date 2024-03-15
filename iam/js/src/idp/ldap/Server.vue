<template>
  <ChcInput
    v-model="store.state.idp.servers[0]"
    label="Server address"
    hint="ldaps://example.hostname:636"
    placeholder="ldaps://server"
    :inputSanitize="
      function (v) {
        return v;
      }
    "
  />
  <ChcInput
    v-model="store.state.idp.servers[1]"
    label="Backup server address"
    hint="Optional"
  />
  <ChcInput
    v-model="store.state.idp.servers[2]"
    label="Backup server address"
    hint="Optional"
  />

  <br v-if="hasLdaps" />
  <b v-if="hasLdaps">TLS verify CA</b>
  <br v-if="hasLdaps" />
  <textarea
    v-if="hasLdaps"
    v-model="store.state.idp.ldapTlsCa"
    :placeholder="fakeCertData"
    rows="10"
  >
  </textarea>
</template>

<script setup>
import { computed } from "vue";
import { useStore } from "vuex";

import ChcInput from "$shared/components/ChcInput.vue";

const store = useStore();

const hasLdaps = computed(() => {
  for (const i in store.state.idp.servers) {
    if (store.state.idp.servers[i].startsWith("ldaps://")) return true;
  }
  return false;
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
