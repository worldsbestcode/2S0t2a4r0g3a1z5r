import axios from "axios";
import { useToast } from "vue-toastification";

import store from "@/store";

const toast = useToast();

const eInjectionStatus = Object.freeze({
  None: 0,
  Running: 1,
  Finished: 2,
  Failed: 3,
});

const eSlotTypes = Object.freeze({
  None: 0,
  Host: 1,
  Firmware: 2,
});

const eHttpsResponse = Object.freeze({
  InvalidRequest: 500,
  Ok: 200,
});

const eServiceResponses = Object.freeze({
  Failure: "Failure",
  Success: "Success",
});

const getDataFromResponse = (state, response) => {
  let data = null;
  if (response.status === eHttpsResponse.Ok) {
    data = response.data;
  } else {
    state.commit("setError", response.message);
  }
  return data;
};

async function getSerialSettings(deviceGroupUuid) {
  let serialSettings = null;
  try {
    const response = await axios.get(`/dki/v1/device/${deviceGroupUuid}`);

    serialSettings = response.data.serialSettings;
  } catch (error) {
    toast.error("Failed to query serial settings");
  }

  return serialSettings;
}

async function updateSerialSettings(deviceGroupUuid, settings) {
  try {
    const response = await axios.patch(
      `/dki/v1/device/${deviceGroupUuid}`,
      settings,
    );
    if (response.status === 200) {
      toast.success("Updated serial settings");
    } else {
      toast.error("Failed to update serial settings");
    }
  } catch (error) {
    toast.error("Failed to update serial settings");
  }
}

async function querySession(sessionUuid, keepAlive) {
  store.dispatch("serviceInfo/querySession", {
    sessionUuid: sessionUuid,
    keepAlive: keepAlive,
  });
}
export {
  eInjectionStatus,
  eSlotTypes,
  eServiceResponses,
  getDataFromResponse,
  updateSerialSettings,
  querySession,
  getSerialSettings,
};
