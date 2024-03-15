import axios from "axios";

const SESSION_TIMEOUT_SEC = 600;
export default {
  namespaced: true,
  state: {
    deviceGroupUuid: null,
    serviceName: "",
    remainingTime: SESSION_TIMEOUT_SEC,
  },
  mutations: {
    setDeviceGroupUuid(state, uuid) {
      state.deviceGroupUuid = uuid;
    },
    setServiceName(state, name) {
      state.serviceName = name;
    },
    setRemainingTime(state, time) {
      state.remainingTime = time;
    },
  },
  getters: {
    getDeviceGroupUuid(state) {
      return state.deviceGroupUuid;
    },
    getServiceName(state) {
      return state.serviceName;
    },
    getRemainingTime(state) {
      return state.remainingTime;
    },
  },
  actions: {
    queryInfo(state, serviceUuid) {
      axios
        .get(`/cuserv/v1/services/${serviceUuid}`, {
          errorContext: "Failed to fetch service",
        })
        .then((response) => {
          state.commit("setServiceName", response.data.objInfo.name);

          let associatedObjects =
            response.data.relatedInfo["associatedObjects"];

          associatedObjects.forEach((associatedObject) => {
            if (associatedObject.type === "SKI device group") {
              state.commit("setDeviceGroupUuid", associatedObject.uuid);
            }
          });
        });
    },
    resetSession(state) {
      state.commit("setRemainingTime", SESSION_TIMEOUT_SEC);
    },
    querySession(state, data) {
      try {
        axios
          .get("/dki/v1/session/query", {
            params: data,
          })
          .then((response) => {
            if (response.status == 200) {
              state.commit("setRemainingTime", response.data.remainingTime);
            }
          });
      } catch (error) {
        console.error(error);
      }
    },
  },
};
