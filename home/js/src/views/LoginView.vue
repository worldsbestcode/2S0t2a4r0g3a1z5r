<template>
  <div class="login-view">
    <div
      class="left__wrapper"
      style="background-image: url(/shared/static/login-left.png)"
    >
      <div class="left">
        <h1>Welcome!</h1>
        <h2>CryptoHub</h2>
        <h3>Encrypt it all, manage it anywhere</h3>
      </div>
    </div>

    <div class="right">
      <div class="right__logo-wrapper">
        <img
          class="right__logo"
          src="/shared/static/crypto-hub-futurex-color.png"
          alt="CryptoHub with Futurex logo"
        />
      </div>

      <div class="right__forms">
        <DummyForms />

        <form
          v-if="!loggedIn && !dfLoginRequired && !expiredUser"
          @keypress.shift.enter.prevent="login({ multi: true })"
          @submit.prevent="login({ multi: false })"
        >
          <p>Identity {{ identityLoginNumber }} login</p>

          <input
            id="username"
            ref="usernameRef"
            v-model="state.username"
            class="chc-input"
            :disabled="state.loading"
            placeholder="Username"
          />

          <input
            id="password"
            v-model="state.password"
            class="chc-input"
            :disabled="state.loading"
            type="password"
            placeholder="Password"
          />

          <div style="margin-top: 2rem">
            <button
              v-if="moreLogins"
              type="button"
              class="button-secondary"
              style="margin-bottom: 0.5rem"
              @click="login({ multi: true })"
            >
              Multi-user login
            </button>

            <button class="button-primary" :disabled="state.loading">
              Log in
            </button>
          </div>
        </form>

        <form v-if="expiredUser" @submit.prevent="changePassword">
          <p>
            Your password for {{ expiredUser.name }} has expired. Enter a new
            password.
          </p>

          <input
            id="password"
            ref="expiredPasswordRef"
            v-model="state.password"
            class="chc-input"
            :disabled="state.loading"
            type="password"
            placeholder="Current password"
          />

          <input
            id="newPassword"
            v-model="state.newPassword"
            class="chc-input"
            :disabled="state.loading"
            type="password"
            placeholder="New password"
          />

          <input
            id="confirmNewPassword"
            v-model="state.confirmNewPassword"
            class="chc-input"
            :disabled="state.loading"
            type="password"
            placeholder="Confirm new password"
          />

          <button class="button-primary" :disabled="state.loading">
            Change password
          </button>
        </form>

        <form
          v-if="!expiredUser && otpLoginRequired"
          @submit.prevent="otpLogin"
        >
          <p>Please enter the one time password from your authenticator app.</p>

          <input
            v-model="state.otp"
            class="chc-input"
            :disabled="state.loading"
            type="text"
            placeholder="One Time Password"
            @input="decimalOtp"
          />

          <button class="button-primary" :disabled="state.loading">
            Log in
          </button>
        </form>

        <CancelButton :loading="state.loading" @cancelled="handleCancel" />
      </div>
    </div>

    <img
      class="red-mountains"
      alt="background image of red mountains"
      src="/shared/static/red-mountains.png"
    />
  </div>
</template>

<script setup>
import axios from "axios";
import {
  computed,
  nextTick,
  onMounted,
  reactive,
  ref,
  watch,
  watchEffect,
} from "vue";
import { useToast } from "vue-toastification";
import { useStore } from "vuex";

import { loginRedirect } from "$shared";
import fxwebauthn from "$shared/utils/fxwebauthn";
import { getHashParams, unwrapErr } from "$shared/utils/web";

import CancelButton from "@/components/CancelButton.vue";
import DummyForms from "@/components/DummyForms.vue";

const store = useStore();
const toast = useToast();

const usernameRef = ref(null);
const expiredPasswordRef = ref(null);

const state = reactive({
  loading: false,
  username: "",
  password: "",
  newPassword: "",
  confirmNewPassword: "",
  error: "",
  loginMore: false,
  otp: "",
});

const loggedIn = computed(() => store.state.auth.fully_logged_in);
const identityLoginNumber = computed(() => store.state.auth.users.length + 1);
const moreLogins = computed(() => store.state.auth.remaining_logins > 1);

const dfLoginRequired = computed(() => store.state.auth.dualFactor);
const otpLoginRequired = computed(
  () => store.state.auth.dualFactor?.method == "OTP",
);

const expiredUser = computed(() =>
  store.state.auth.users.find((user) => user.expired && !user.defaultPw),
);

const loginUrl = "/home/v1/login";

function focusInput() {
  if (usernameRef.value) {
    usernameRef.value.focus();
  }
  if (expiredPasswordRef.value) {
    expiredPasswordRef.value.focus();
  }
}

function requestFinished() {
  state.loading = false;
  nextTick(focusInput);
}

function handleCancel() {
  state.loading = true;
  state.error = "";
  state.username = "";
  state.password = "";
  requestFinished();
}

function decimalOtp(event) {
  state.otp = event.target.value.replace(/[^0-9.]/g, "");
}

function login({ multi = false } = {}) {
  state.loading = true;
  state.error = "";

  const loginBody = {
    authType: "userpass",
    authCredentials: {
      username: state.username,
      password: btoa(state.password),
      multiLogin: multi,
    },
  };
  axios
    .post(loginUrl, loginBody)
    .then(async (response) => {
      store.commit("auth/login", response.data);

      const fidoResponse = await fidoLogin(response.data);
      if (fidoResponse) {
        store.commit("auth/login", fidoResponse.data);
      }

      state.username = "";
      state.password = "";
    })
    .catch((error) => {
      state.error = unwrapErr(error);
      state.password = "";
    })
    .finally(requestFinished);
}

function otpLogin() {
  state.loading = true;
  state.error = "";
  const loginBody = {
    authType: "otp",
    authCredentials: {
      password: state.otp,
    },
  };
  axios
    .post(loginUrl, loginBody)
    .then(async (response) => {
      store.commit("auth/login", response.data);
      state.otp = "";
      toast.success("OTP login complete");
    })
    .catch((error) => {
      state.error = unwrapErr(error);
      state.otp = "";
      toast.error("OTP login failed.");
      store.dispatch("auth/reload");
    })
    .finally(requestFinished);
}

async function fidoLogin(auth) {
  const dualFactor = auth.dualFactor;
  if (dualFactor && dualFactor.method == "U2F") {
    toast("FIDO login required");
    try {
      let attestation;
      // Login through cardbrowser / securus
      if (window.fxctx && window.fxctx.fido) {
        // Wait for toast to pop up
        await new Promise((r) => setTimeout(r, 500));

        const result = await window.fxctx.fido.loginFxFido(
          dualFactor.nonce,
          dualFactor.credential,
          dualFactor.origin,
        );
        if (result.success) {
          attestation = window.btoa(result.value);
        } else {
          toast.error(
            "FIDO login failed: " +
              result.msg +
              "\nRefresh the page to try again",
          );
        }
      }
      // Remote login
      else {
        attestation = await fxwebauthn.authenticateCredential(
          dualFactor.nonce,
          dualFactor.credential,
        );
      }

      // Post to login endpoint
      if (attestation) {
        const response = await axios.post(loginUrl, {
          authType: "fido",
          authCredentials: {
            response: attestation,
          },
        });
        toast.success("FIDO login complete");
        return response;
      }
    } catch {
      toast.error("FIDO login failed. Refresh the page to try again");
    }
  }
}

function changePassword() {
  if (state.newPassword !== state.confirmNewPassword) {
    state.error =
      "Failed to change password: new password confirmation does not match new password.";
    return;
  }

  state.loading = true;
  state.error = "";

  axios
    .post("/home/v1/changepw", {
      username: expiredUser.value.name,
      oldPassword: btoa(state.password),
      newPassword: btoa(state.newPassword),
    })
    .then((response) => {
      store.commit("auth/login", response.data);

      state.username = "";
      state.password = "";
      state.newPassword = "";
      state.confirmNewPassword = "";
    })
    .catch((error) => {
      state.error = unwrapErr(error);
    })
    .finally(requestFinished);
}

async function loginJwt() {
  // Logging in an iframe or redirect
  const hashParams = getHashParams();
  const jwt = hashParams.jwt;
  if (jwt) {
    await store.dispatch("auth/tokenLogin", jwt);
    await store.dispatch("auth/reload");
  }
}

onMounted(async () => {
  focusInput();

  const auth = store.state.auth;
  const response = await fidoLogin(auth);
  if (response) {
    store.commit("auth/login", response.data);
  }

  axios.get("/logout").catch(() => {}); // Force logout HSM web

  loginJwt();
});

watchEffect(() => {
  if (state.error) {
    toast.error(state.error);
    state.error = "";
  }
});

watch(
  () => store.state.auth.fully_logged_in,
  () => {
    loginRedirect(store);
  },
);
</script>

<style>
.login-view {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

@media (max-width: 1250px) {
  .left__wrapper {
    display: none;
  }
}

.left__wrapper {
  color: var(--primary-background-color);
  background-repeat: no-repeat;
  background-color: #131212;

  max-width: 800px;
  padding-left: 2rem;
  padding-right: 2rem;

  flex-grow: 1;
  flex-shrink: 0;
}

.left {
  background: radial-gradient(
    50% 50% at 50% 50%,
    rgba(0, 0, 0, 0.86) 0%,
    rgba(0, 0, 0, 0) 100%
  );
  width: fit-content;
  margin-top: 9rem;
  margin-left: auto;
  margin-right: auto;
}

.right {
  padding-left: 2rem;
  padding-right: 2rem;

  flex-grow: 1;

  display: grid;

  grid-template-rows: max-content 1fr;

  overflow: auto;
  padding-bottom: 2rem;
}

.right__logo {
  display: block;
  margin-top: 4rem;
  margin-left: auto;
  margin-right: auto;
  max-width: 450px;
  width: 100%;
}

.right__logo-wrapper {
  min-height: 200px;
  max-height: 400px;
}

.right__forms {
  display: grid;
  grid-template-rows: repeat(10, max-content);
  grid-template-columns: minmax(auto, 660px);
  justify-content: center;
}

.right__forms p {
  margin-bottom: 0.5rem;
}

.right__forms form + form {
  margin-top: 1rem;
}

.right__forms form:last-child {
  margin-top: 0.5rem;
}

.right__forms .chc-input {
  max-width: 660px;
  min-width: unset;
  height: 44px;
}

.right__forms .chc-input + .chc-input,
.right__forms .chc-input + .button-primary {
  margin-top: 0.5rem;
}

.right__forms .button-primary,
.right__forms .button-secondary {
  max-width: 660px;
  width: 100%;
  height: 44px;
}

.right__forms .chc-radio {
  height: 44px;
  margin-bottom: 0.5rem;
  justify-content: center;
}

.red-mountains {
  position: fixed;
  right: 0;
  bottom: 0;
  z-index: -1;

  width: 510px;
  height: 236px;
}

h1 {
  font-size: 96px;
  font-weight: 500;
}

h2 {
  font-size: 40px;
  font-weight: 400;
}

h3 {
  font-weight: 400;
  font-size: 28px;
}
</style>
