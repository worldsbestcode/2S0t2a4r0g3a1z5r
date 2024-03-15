import axios from "axios";
import { unwrapErr } from "@/utils/web";

export default {
  namespaced: true,
  state: {
    devices: [],
    ports: [],
    error: null,
  },
  mutations: {
    setPorts(state, ports) {
      state.ports = ports;
    },
    setError(state, error) {
      state.error = unwrapErr(error);
    },
    removePort(state, uuid) {
      for (let id in state.ports) {
        if (state.ports[id].obj_info.uuid == uuid) {
          state.ports.splice(id, 1);
          break;
        }
      }
    },
    changePort(state, data) {
      for (let id in state.ports) {
        if (state.ports[id].obj_info.uuid == data.obj_info.uuid) {
          state.ports.splice(id, 1);
          break;
        }
      }
      state.ports.push(data);
    },
  },
  actions: {
    // Load basic information about all ports
    async getPortStubs(state) {
      try {
        // Get balancer port stubs
        axios.get("/v1/balancingPorts/list").then(function (res) {
          state.commit("setPorts", res.data.results);
        });
        // Handle error
      } catch (err) {
        state.commit("setError", err);
      }
    },
    removePort(state, uuid) {
      state.commit("removePort", uuid);
    },
    portChanged(state, data) {
      state.commit("changePort", data);
    },
  },
};
