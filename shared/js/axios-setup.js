import axios from "axios";
import { useToast } from "vue-toastification";

import { sendToLogin } from "$shared";
import { bus } from "$shared/bus.js";

const toast = useToast();

function configureXsrf() {
  axios.defaults.xsrfCookieName = "FXSRF-TOKEN";
  axios.defaults.xsrfHeaderName = "X-FXSRF-TOKEN";
}

function addLoadingInterceptors() {
  function setLoading(config, value) {
    if (config?.loading) {
      config.loading.value = value;
    }
  }

  function fail(error) {
    const config = error.config;
    setLoading(config, false);
    return Promise.reject(error);
  }

  axios.interceptors.request.use((config) => {
    setLoading(config, true);
    return config;
  }, fail);

  axios.interceptors.response.use((response) => {
    const config = response.config;
    setLoading(config, false);
    return response;
  }, fail);
}

function addAuthInterceptors() {
  axios.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      const response = error.response;

      if (response.config.ignoreAuth) {
        return;
      }

      if (response) {
        if (response.status === 401) {
          sendToLogin({ shouldContinue: true });
        }
      }

      return Promise.reject(error);
    }
  );
}

// Flask Marshmallow style errors
function serializeMarshmallowError(data) {
  if (!data) return "";

  function serializeRecursive(data) {
    let result = "";

    for (const key in data) {
      if (Array.isArray(data[key])) {
        const errorMessages = data[key].join(", ");
        result += `${key}: ${errorMessages}\n`;
      } else if (typeof data[key] === "object" && data[key] !== null) {
        result += serializeRecursive(data[key]);
      }
    }

    return result;
  }

  return serializeRecursive(data);
}

function addErrorToastInterceptors() {
  axios.interceptors.response.use(
    (response) => {
      const config = response.config;
      if (config.emit) {
        bus.emit(config.emit);
      }
      return response;
    },
    (error) => {
      const response = error.response;
      const config = error.config;

      if (response) {
        const data = response.data;
        if (!config.silenceToast) {
          const errorContext = config.errorContext;
          let apiMessage = data.message;
          let mmError = serializeMarshmallowError(data.errors);

          let toastMessage = "";
          if (errorContext) {
            toastMessage += errorContext;
          }
          if (errorContext && apiMessage) {
            toastMessage += ": ";
          }
          if (apiMessage) {
            toastMessage += apiMessage;
          }
          if (toastMessage && mmError) {
            toastMessage += "\n";
          }
          if (mmError) {
            toastMessage += mmError;
          }
          if (toastMessage === "") {
            toastMessage = "Unexpected error";
          }

          toast.error(toastMessage);
        }
        return Promise.reject(Error(data.message));
      } else {
        return Promise.reject(Error("request failed"));
      }
    }
  );
}

export function configureAxios({
  xsrf = true,
  loading = true,
  auth = true,
  error = true,
} = {}) {
  if (xsrf) {
    configureXsrf();
  }
  if (loading) {
    addLoadingInterceptors();
  }
  if (auth) {
    addAuthInterceptors();
  }
  if (error) {
    addErrorToastInterceptors();
  }
}
