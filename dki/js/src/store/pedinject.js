import axios from "axios";
import { reactive } from "vue";
import BigInt from "big-integer";
import {
  eInjectionStatus,
  eServiceResponses,
  getDataFromResponse,
} from "../utils/common.js";

export default {
  namespaced: true,
  state: {
    devices: reactive([]),
    sessionId: null,
    error: null,
    injectionStatusMap: reactive({}), // this is the map that will hold the injection status
    service_id: null,
    logMessages: reactive([]),
    pagination: reactive({
      page: 1,
      pageSize: 5,
      totalPages: 1,
    }),
    supportedFeatures: {
      canWriteSerialNumber: false,
      canReadSerialNumber: false,
      canPrint: false,
    },
  },
  mutations: {
    /**
     * This function will set the devices in the store
     *
     * @param {*} state - the state of the store
     * @param {*} data - the devices to be set
     */
    setDevices(state, data) {
      data.slots.forEach((device) => {
        let deviceId = BigInt(device.id);
        const oldDevice = state.devices.find(
          (item) => item.id.value === deviceId.value,
        );

        if (oldDevice) {
          device.selected = oldDevice.selected;
        }
      });

      state.devices = data.slots;

      state.devices.forEach((device) => {
        device.id = BigInt(device.id);
      });

      state.devices.sort((left, right) => {
        return left.type - right.type;
      });

      state.devices.sort((left, right) => {
        return left.cardIndex - right.cardIndex;
      });

      state.devices.sort((left, right) => {
        return left.slotIndex - right.slotIndex;
      });
    },
    addLogMessages(state, logMessages) {
      let oldMessages = state.logMessages;
      state.logMessages = oldMessages.concat(logMessages);
    },

    /**
     * This function will set the session id in the store
     *
     * @param {*} state - the state of the store
     * @param {*} sessionId - the session id to be set
     */
    setSessionId(state, sessionId) {
      state.sessionId = sessionId;
    },
    setServiceId(state, serviceId) {
      state.serviceId = serviceId;
    },
    /**
     * This function will set the error in the store
     *
     * @param {*} state - the state of the store
     * @param {*} error - the error to be set
     */
    setError(state, error) {
      state.error = error;
    },

    updateDevices(state, data) {
      state.devics = [];
      state.devices = data.devices;
    },

    updateDevice(state, data) {
      let device = data.device;
      const index = state.devices.findIndex((d) => d.id === device.id);
      if (index === -1) {
        return;
      }

      state.devices.splice(index, 1, device);
    },

    /**
     * This function will update the injection status for a given slot
     *
     * @param {*} state - the state of the store
     * @param {*} statusInfo - the status info to be updated
     */
    setInjectionStatus(state, statusInfo) {
      // this is the mutation that will update the injection status
      state.injectionStatusMap = reactive({
        ...state.injectionStatusMap,
        [statusInfo["deviceId"]]: statusInfo["result"],
      });
    },
    setPagination(state, pagination) {
      state.pagination = reactive({
        ...state.pagination,
        ...pagination,
      });
    },
    /**
     * This function will update the supported features
     *
     * @param {*} state - the state of the store
     * @param {*} features - the features to be updated
     */
    setSupportedFeatures(state, features) {
      state.supportedFeatures = reactive({
        ...state.supportedFeatures,
        ...features,
      });
    },
  },
  getters: {
    getDevices(state) {
      return state.devices;
    },
    getSupportedFeatures(state) {
      return state.supportedFeatures;
    },
    getSessionId(state) {
      return state.sessionId;
    },
    getError(state) {
      return state.error;
    },
    getServiceId(state) {
      return state.serviceId;
    },
    getInjectionStatusMap(state) {
      return state.injectionStatusMap;
    },
    getLogMessages(state) {
      return state.logMessages;
    },
    getPagination(state) {
      return state.pagination;
    },
  },
  actions: {
    /**
     * This function will get the list of devices from the ped inject service
     *
     * @param {*} state - the state of the store
     * @param {*} sessionId - the session id to be passed to the API
     */
    async getSlots(state, sessionId) {
      try {
        const response = await axios.get("/dki/v1/slots/query", {
          params: {
            session: String(sessionId),
          },
        });
        const data = getDataFromResponse(state, response);

        if (data) {
          if (data.status === eServiceResponses.Success) {
            state.commit("setDevices", data);
          } else {
            state.commit("setError", data.message);
          }
        }
      } catch (error) {
        state.commit("setError", error);
      }
    },

    /**
     * This function will start a session with the ped inject service
     *
     * @param {*} state - the state of the store
     * @param {*} params - the parameters to be passed to the API
     */
    async startSession(state, params) {
      let sessionId = null;
      try {
        const response = await axios.post("/dki/v1/session/start", params);

        const data = getDataFromResponse(state, response);
        if (data) {
          if (data.status === eServiceResponses.Success) {
            sessionId = data.session;
            state.commit("setSessionId", sessionId);
          } else {
            state.commit("setError", data.message);
          }
        }
      } catch (error) {
        state.commit("setError", error);
      }
      return sessionId;
    },

    /**
     * This function will get the serial number from the device
     *
     * @param {*} state - the state of the store
     * @param {*} params - the parameters to be passed to the API
     */
    async getSerialNumber(state, params) {
      let serialInfo = {
        serialNumber: null,
        displaySerialPrompt: false,
        displayErrorOnCancel: true,
        error: null,
      };
      let injectionStatus = eInjectionStatus.Running;

      state.commit("setInjectionStatus", {
        deviceId: params.slot_id,
        result: {
          status: eInjectionStatus.Running,
          message: null,
        },
      });
      try {
        const response = await axios.post("/dki/v1/inject/serial", params);

        let data = getDataFromResponse(state, response);
        if (data) {
          if (data.status === eServiceResponses.Success) {
            serialInfo.serialNumber = data.serial_number;
            serialInfo.displaySerialPrompt = data.display_serial_prompt;
          } else {
            state.commit("setError", response.data.message);
            serialInfo.error = response.data.message;
          }
        }
      } catch (error) {
        state.commit("setError", error.message);
        serialInfo.error = error.message;
      }

      state.commit("setInjectionStatus", {
        deviceId: params.slot_id,
        result: {
          status: injectionStatus,
          message: null,
        },
      });
      return serialInfo;
    },

    /**
     * This function will start the injection of keys into the device
     *
     * @param {*} state - the state of the store
     * @param {*} params - the parameters to be passed to the API
     */
    async injectTerminal(state, params) {
      try {
        const response = await axios.post("/dki/v1/inject/start", params);

        const data = getDataFromResponse(state, response);
        if (data) {
          if (data.status === eServiceResponses.Success) {
            state.commit("setInjectionStatus", {
              deviceId: params.slot_id,
              result: {
                status: eInjectionStatus.Running,
                message: null,
              },
            });
          } else {
            state.commit("setError", data.message);
          }
        }
      } catch (error) {
        state.commit("setError", error);
      }
    },

    /**
     * This function will query the injection status for a given slot
     *
     * @param {*} state - the state of the store
     * @param {*} params - the parameters to be passed to the API
     */
    async queryInjection(state, params) {
      let status = eInjectionStatus.None;
      let message = null;
      let logMessages = [];
      try {
        const response = await axios.get("/dki/v1/inject/status", {
          params: params,
        });

        const data = getDataFromResponse(state, response);
        if (data) {
          if (data.message === eServiceResponses.Success) {
            if (data.messages.length > 0) {
              message = data.messages[0];
            }
            logMessages = data.logMessages;
            status = data.status;
          } else {
            state.commit("setError", data.message);
            status = eInjectionStatus.Failed;
          }
        } else {
          status = eInjectionStatus.Failed;
        }
      } catch (error) {
        state.commit("setError", error);
        status = eInjectionStatus.Failed;
      }

      state.commit("setInjectionStatus", {
        deviceId: params.slot_id,
        result: {
          status: status,
          message: message,
        },
      });

      state.commit("addLogMessages", logMessages);
    },

    async updateDevice(state, data) {
      state.commit("updateDevice", data);
    },

    async updateDevices(state, data) {
      state.commit("updateDevices", data);
    },
    async setServiceId(state, serviceId) {
      state.commit("setServiceId", serviceId);
    },

    async setPagination(state, pagination) {
      state.commit("setPagination", pagination);
    },
  },
};
