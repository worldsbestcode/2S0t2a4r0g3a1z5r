import axios from "axios";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useAdminServicesStore = defineStore("adminServices", () => {
  const loading = ref(false);
  const categories = ref([]);

  const services = computed(() => categories.value.flatMap((x) => x.services));

  loading.value = true;
  axios
    .get("/home/v1/dashboard/services", {
      errorContext: "Failed to fetch admin services",
    })
    .then((response) => {
      categories.value = response.data.categories;
    })
    .finally(() => (loading.value = false));

  return { loading, categories, services };
});
