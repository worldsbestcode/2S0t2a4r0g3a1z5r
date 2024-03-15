import axios from "axios";
import { defineStore } from "pinia";
import { ref } from "vue";

export const useDeployedServicesStore = defineStore("deployedServices", () => {
  const loading = ref(false);
  const services = ref([]);

  async function addServiceByUuid(serviceUuid) {
    return axios.get(`/cuserv/v1/services/${serviceUuid}`).then((response) => {
      services.value.push(response.data);
    });
  }

  function removeServiceByUuid(serviceUuid) {
    const serviceIndex = services.value.findIndex(
      (x) => x.objInfo.uuid === serviceUuid,
    );
    services.value.splice(serviceIndex, 1);
  }

  function refreshServiceByUuid(serviceUuid) {
    // Only remove existing service if we successfully add a new service to the store
    addServiceByUuid(serviceUuid).then(() => removeServiceByUuid(serviceUuid));
  }

  loading.value = true;
  axios
    .get("/cuserv/v1/services/stubs", {
      params: {
        page: 1,
        pageSize: 100,
      },
      errorContext: "Failed to fetch deployed services",
      loading,
    })
    .then((response) => {
      services.value = response.data.results;
    })
    .finally(() => (loading.value = false));

  return {
    loading,
    services,
    addServiceByUuid,
    removeServiceByUuid,
    refreshServiceByUuid,
  };
});
