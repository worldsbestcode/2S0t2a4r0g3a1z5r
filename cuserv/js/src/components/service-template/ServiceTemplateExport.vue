<template>
  <LoadingSpinner :loading="loading" />
  <button :disabled="loading" @click="exportTemplate(props.uuid, props.name)">
    Export
  </button>
</template>

<script setup>
import axios from "axios";
import { defineProps, ref } from "vue";
import { useToast } from "vue-toastification";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

const toast = useToast();

const props = defineProps({
  uuid: {
    type: String,
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

async function exportTemplate(uuid, name) {
  axios
    .get(`/cuserv/v1/templates/export/${uuid}`, {
      errorContext: "Failed to export template",
      loading,
    })
    .then((response) => {
      const templateData = response.data.template_data;
      const templateDataJson = atob(templateData);

      const a = document.createElement("a");
      const blobUrl = window.URL.createObjectURL(
        new Blob(templateDataJson.split("")),
      );
      a.href = blobUrl;
      a.download = `${name}-template.json`;
      a.click();
      window.URL.revokeObjectURL(blobUrl);

      toast("Exported template");
    });
}
</script>
