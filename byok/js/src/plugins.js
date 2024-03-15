import axios from "axios";
import mitt from "mitt";
import { clusterSessionExpired, sessionIdFromUri } from "@/utils/misc.js";

const bus = mitt();

let httpV2 = axios.create({
  baseURL: "/byok/v1",
  headers: {
    "Content-Type": "application/json",
  },
  xsrfCookieName: "FXSRF-TOKEN",
  xsrfHeaderName: "X-FXSRF-TOKEN",
});

httpV2.interceptors.response.use(
  handleSuccessfulResponse,
  handleUnsuccessfulResponse,
);

function handleSuccessfulResponse(response) {
  let data = response.data;
  if (data.status === "Success") {
    if (data.response) {
      return data.response;
    } else {
      return {};
    }
  } else {
    if (data.includes("window.location = '/'")) {
      window.location = "/";
    }
    return Promise.reject(Error("response is invalid"));
  }
}

async function handleUnsuccessfulResponse(error) {
  let response = error.response;
  if (response) {
    let data = response.data;
    switch (data.message) {
      case "Invalid CSRF token.":
      case "User not authenticated.":
        alert("Session has expired");
        try {
          await httpV2.post("/byok/v1/logout");
        } finally {
          location.replace("/");
        }
        break;
      case "Attempted to access unknown connection.":
        var sessionId =
          error.request &&
          error.request.responseURL &&
          sessionIdFromUri(error.request.responseURL);
        if (sessionId) await httpV2.delete(`/clusters/sessions/${sessionId}`);
      // fall through
      case "User not logged in":
        clusterSessionExpired();
        return Promise.reject(Error("not logged in to cluster"));
      default:
        if (!error.config.silenceToastError) {
          let contextMessage = error.config.errorContextMessage;
          let apiMessage = data.message;

          let toastMessage = "";

          if (contextMessage) {
            toastMessage += contextMessage;
          }

          if (contextMessage && apiMessage) {
            toastMessage += ": ";
          }

          if (apiMessage) {
            toastMessage += apiMessage;
          }

          if (toastMessage === "") {
            toastMessage = "Unexpected error";
          }

          bus.emit("toaster", { message: toastMessage, type: "error" });
        }
        return Promise.reject(Error(data.message));
    }
  } else {
    return Promise.reject(Error("request failed"));
  }
}

export { bus, httpV2 };
