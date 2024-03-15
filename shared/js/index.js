import { adminSetupsOrder } from "$shared/admin.js";

import "$shared/style/shared.css";
import "../static/material-icons/material-icons-outlined.css";

import axios from "axios";

axios.defaults.xsrfCookieName = "FXSRF-TOKEN";
axios.defaults.xsrfHeaderName = "X-FXSRF-TOKEN";

const cryptoHubLoginPath = "/";

function continueUrl() {
  const pathname = window.location.pathname;
  const hash = window.location.hash;
  return encodeURIComponent(`${pathname}${hash}`);
}

export function sendToLogin({ shouldContinue = false } = {}) {
  if (shouldContinue) {
    alert("Session expired/not logged in, redirecting to login page");
    window.location.replace(`${cryptoHubLoginPath}?continue=${continueUrl()}`);
  } else {
    window.location.replace(cryptoHubLoginPath);
  }
}

async function attemptSetupPendingRedirect(store, auth) {
  if (!auth.perms.includes("System:Administration")) {
    return;
  }

  // todo: figure out a way to determine if this already exists from the router setup store initialization
  await store.dispatch("notifications/initialize");
  const setupNotifications = store.getters["notifications/setupPending"];

  for (const setupType of adminSetupsOrder) {
    if (setupNotifications.includes(setupType)) {
      window.location.replace("/admin/#/setup");
      return true;
    }
  }
}

async function attemptGoogleCseKeysRedirect(auth) {
  const googleCsePermissions =
    auth.auth_perms.length == 3 &&
    auth.auth_perms.includes("Google CSE:Client") &&
    auth.auth_perms.includes("Keys") &&
    auth.auth_perms.includes("Keys:Personal Keys");

  if (googleCsePermissions) {
    await axios
      .get("/gcse/v1/users/lookup")
      .then((response) => {
        const data = response.data;

        window.location.replace(
          `/cuserv/#/deployed/${data.serviceUuid}/users/${data.userUuid}/keys`
        );
      })
      .catch(() => {});
    return true;
  }
}

function attemptContinueUrlRedirect() {
  function getContinueUrl() {
    const url = new URL(window.location);
    return url.searchParams.get("continue");
  }

  const continueUrl = getContinueUrl();
  if (continueUrl) {
    window.location.replace(continueUrl);
    return true;
  }
}

export async function loginRedirect(store) {
  const auth = store.state.auth;

  const expiredUser = store.state.auth.users.find(
    (user) => user.expired && !user.defaultPw
  );
  if (!auth.fully_logged_in || expiredUser) {
    return;
  }

  const defaultPw = store.state.auth.users.some((user) => user.defaultPw);
  if (defaultPw) {
    window.location.replace("/admin/#default");
    return;
  }

  if (await attemptSetupPendingRedirect(store, auth)) {
    return;
  }

  if (await attemptGoogleCseKeysRedirect(auth)) {
    return;
  }

  if (attemptContinueUrlRedirect()) {
    return;
  }

  window.location.replace("/cuserv/");
}

export async function initializeSharedStores(store) {
  if (store.state.shared.loaded) {
    return;
  }

  await store.dispatch("auth/reload");

  const loggedIn = store.state.auth.fully_logged_in;
  const defaultPw = store.state.auth.users.some((user) => {
    return user.defaultPw;
  });

  if (loggedIn && window.location.pathname === cryptoHubLoginPath) {
    await loginRedirect(store);
  }

  if (loggedIn && !defaultPw) {
    await store.dispatch("profiles/initialize");

    const hasNotificationsPermissions = store.state.auth.perms.includes(
      "System:Administration"
    );
    if (hasNotificationsPermissions) {
      await store.dispatch("notifications/initialize");
    }
  }

  store.commit("setLoaded", true);
}
