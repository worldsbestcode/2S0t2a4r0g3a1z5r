<template>
  <!-- Credentials table -->
  <table v-if="mode == 'form' && !isNewUser()">
    <!-- Application authentication type -->
    <tr v-if="store.state.user.application">
      <td colspan="2">
        <ChcComboBox
          v-model="store.state.user.authType"
          label="Authentication Type"
          :values="authTypes"
        />
      </td>
    </tr>
    <!-- Choose Password/Default -->
    <tr
      v-if="
        store.state.user.authType === 'P' || store.state.user.authType === 'N'
      "
    >
      <td>
        Last changed:<br />
        {{ store.state.user.passChangedTime }}
      </td>
      <td>
        <ChcButton
          class="edit-button"
          img="/shared/static/pencil-active.svg"
          @click="mode = 'password'"
          >PASSWORD</ChcButton
        >
      </td>
    </tr>
    <!-- Choose API key -->
    <tr v-if="store.state.user.authType === 'A'">
      <td>
        Last changed:<br />
        {{ store.state.user.apiKeyChangedTime }}
      </td>
      <td>
        <ChcCheckBox
          v-model="store.state.user.newApiKey"
          :disabled="!store.state.user.hasApiKey"
          hint=""
          label="Issue new"
        />
      </td>
    </tr>
    <!-- Choose FIDO -->
    <tr v-if="showDf()">
      <td>{{ fidoInfo() }}</td>
      <td>
        <ChcButton
          class="edit-button"
          img="/shared/static/pencil-active.svg"
          @click="
            mode = 'fido';
            store.state.user.newFidoName = '';
          "
          >FIDO</ChcButton
        >
      </td>
    </tr>
    <!-- Choose OTP -->
    <tr v-if="showDf() && store.state.user.hardened == false">
      <td>{{ otpInfo() }}</td>
      <td>
        <ChcButton
          class="edit-button"
          img="/shared/static/pencil-active.svg"
          @click="mode = 'otp'"
          >OTP</ChcButton
        >
      </td>
    </tr>
    <!-- Choose TLS -->
    <tr v-if="store.state.user.authType === 'T'">
      <td colspan="2">
        <ChcComboBox
          v-model="store.state.user.tlsProvider"
          :label="tlsIdpLabel"
          :values="store.state.user.tlsProviders"
        />
      </td>
    </tr>
    <!-- Choose JWT -->
    <tr v-if="store.state.user.authType === 'J'">
      <td colspan="2">
        <ChcComboBox
          v-model="store.state.user.jwtProvider"
          :label="jwtIdpLabel"
          :values="store.state.user.jwtProviders"
        />
      </td>
    </tr>
  </table>

  <!-- Password change form -->
  <div v-if="mode == 'password' || isNewUser()">
    <ChcInput
      v-model="store.state.user.newPassword"
      hint=""
      label="New Password"
      placeholder="Password"
      type="password"
    />
    <ChcInput
      v-model="store.state.user.repeatPassword"
      hint=""
      label="Repeat Password"
      placeholder="Repeat Password"
      type="password"
    />
    <ChcCheckBox
      v-model="store.state.user.passwordChange"
      hint=""
      label="Require password change"
      type="password"
    />
  </div>

  <!-- Manage OTP Token -->
  <div v-if="mode == 'otp'">
    <!-- Register OTP -->
    <div v-if="store.state.user.otpToken === null">
      <form
        v-if="store.state.user.otpSessionId === null"
        @submit.prevent="generateOtp()"
      >
        <ChcButton class="edit-button" img="/shared/static/pencil-active.svg"
          >GENERATE</ChcButton
        >
      </form>
      <div v-if="store.state.user.otpSessionId !== null">
        <ChcInput
          v-model="store.state.user.otpVerify"
          hint=""
          label="Verify OTP"
          placeholder="One Time Password"
        />
        <br />
      </div>
      <div ref="qrCodeRef"></div>
    </div>
    <!-- Unregister OTP -->
    <div v-else>
      <form @submit.prevent="unregisterOtp()">
        <ChcButton class="edit-button" img="/shared/static/trash-active.svg"
          >UNREGISTER</ChcButton
        >
      </form>
    </div>
  </div>

  <!-- Manage FIDO Token -->
  <div v-if="mode == 'fido'">
    <!-- Register FIDO -->
    <div v-if="store.state.user.fidoToken === null">
      <ChcInput
        v-model="store.state.user.newFidoName"
        hint=""
        label="Token Name"
        placeholder="Name"
      />
    </div>
    <!-- Unregister FIDO -->
    <div v-else>
      <form @submit.prevent="unregisterFido()">
        <ChcButton class="edit-button" img="/shared/static/trash-active.svg"
          >UNREGISTER</ChcButton
        >
      </form>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import QRCode from "davidshimjs-qrcodejs";
import { computed, defineEmits, defineProps, reactive, ref } from "vue";
import { useToast } from "vue-toastification";
import { useStore } from "vuex";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcInput from "$shared/components/ChcInput.vue";

import ChcCheckBox from "@/components/ChcCheckBox.vue";

const toast = useToast();

const store = useStore();

const showDf = () => {
  return store.state.user.uuid !== null && !store.state.user.application;
};
const isNewUser = () => {
  return store.state.user.uuid === null && !store.state.user.application;
};

// XXX: This matches the definitions in RKRI
const authTypes = computed(() => {
  let ret = [
    { value: "N", label: "None" },
    { value: "A", label: "API Key" },
    { value: "P", label: "Password" },
  ];
  if (!store.state.user.hardened) {
    ret.push({ value: "T", label: "TLS Certificate" });
    ret.push({ value: "J", label: "JSON Web Token" });
  }
  return ret;
});

const tlsIdpLabel = computed(() => {
  let ret = "TLS Provider";
  if (store.state.user.tlsProviders.length <= 1)
    ret += " (No providers configured)";
  return ret;
});

const jwtIdpLabel = computed(() => {
  let ret = "JWT Provider";
  if (store.state.user.jwtProviders.length <= 1)
    ret += " (No providers configured)";
  return ret;
});

const mode = ref("form");
const qrCodeRef = ref(null);
const fidoName = ref("");

function otpInfo() {
  if (store.state.user.otpToken) {
    return "Loaded: " + store.state.user.otpToken;
  }
  return "Not loaded";
}

async function generateOtp() {
  try {
    const challenge = await axios.get("/iam/v1/otp/register/" + props.uuid);
    store.state.user.otpSessionId = challenge.data.sessionId;

    var elem = new QRCode(qrCodeRef.value, {
      text: challenge.data.uri,
      // XXX: Better way than a static pixel size?
      width: 500,
      height: 500,
      colorDark: "#000000",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.H,
    });
  } catch (err) {
    // Axios should toast
  }
}

async function unregisterOtp() {
  try {
    await axios.delete("/iam/v1/otp/tokens/" + props.uuid);
    store.state.user.otpToken = null;
    toast.success("Remove OTP token.");
  } catch (err) {
    // Axios should toast
  }
}

function fidoInfo() {
  if (store.state.user.fidoToken) {
    return "Loaded: " + store.state.user.fidoToken;
  }
  return "Not loaded";
}

async function unregisterFido() {
  try {
    await axios.delete(
      "/iam/v1/fido/tokens/" + props.uuid + "/" + store.state.user.fidoToken,
    );
    store.state.user.fidoToken = null;
    store.state.user.newFidoName = null;
    toast.success("Remove FIDO token.");
  } catch (err) {
    // Axios should toast
  }
}

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
});
</script>

<style scoped>
.edit-button {
  width: 15rem;
}
td {
  padding: 1rem;
}
</style>
