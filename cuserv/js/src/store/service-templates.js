import axios from "axios";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

function groupServiceTemplatesByCategory(serviceTemplates) {
  const categoriesAndServices = {};

  for (const serviceTemplate of serviceTemplates) {
    for (const category of serviceTemplate.params.details.categories) {
      if (!categoriesAndServices[category]) {
        categoriesAndServices[category] = [];
      }

      if (!categoriesAndServices[category].includes(serviceTemplate)) {
        categoriesAndServices[category].push(serviceTemplate);
      }
    }
  }

  for (const services of Object.values(categoriesAndServices)) {
    services.sort((a, b) => a.objInfo.name.localeCompare(b.objInfo.name));
  }

  const categorySortOrder = Object.keys(categoriesAndServices).sort((a, b) => {
    // Makes Home the first category
    if (a === "Home") {
      return -1;
    }

    return a.localeCompare(b);
  });

  const categoriesAndServicesSorted = {};
  for (const category of categorySortOrder) {
    categoriesAndServicesSorted[category] = categoriesAndServices[category];
  }

  return categoriesAndServicesSorted;
}

export const useServiceTemplatesStore = defineStore("serviceTemplates", () => {
  const loading = ref(false);
  const all = ref([]);
  const byCategory = computed(() => groupServiceTemplatesByCategory(all.value));

  function addServiceTemplateByUuid(uuid) {
    axios
      .get(`/cuserv/v1/templates/${uuid}`, {
        errorContext: "Failed to fetch service template",
        loading,
      })
      .then((response) => {
        delete response.data.message;
        delete response.data.status;
        all.value.push(response.data);
      });
  }

  loading.value = true;
  axios
    .get("/cuserv/v1/templates/stubs", {
      params: {
        page: 1,
        pageSize: 100,
      },
      errorContext: "Failed to fetch service templates",
    })
    .then((response) => {
      all.value = response.data.results;
    })
    .finally(() => (loading.value = false));

  return { loading, all, byCategory, addServiceTemplateByUuid };
});
