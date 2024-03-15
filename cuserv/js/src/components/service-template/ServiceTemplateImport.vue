<template>
  <LoadingSpinner :loading="loading" />

  <input
    v-show="false"
    ref="templateFileInput"
    type="file"
    @change="handleTemplateFileSelected"
  />
  <button
    class="chc-main-link"
    :disabled="loading"
    @click="templateFileInput.click()"
  >
    Import Template
  </button>
</template>

<script setup>
import axios from "axios";
import { ref } from "vue";
import { useToast } from "vue-toastification";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

import { useServiceTemplatesStore } from "@/store/service-templates";

const toast = useToast();
const serviceTemplatesStore = useServiceTemplatesStore();

const templateFileInput = ref(null);

const loading = ref(false);

async function handleTemplateFileSelected(event) {
  const templateFile = event.target.files[0];
  const templateFileContents = await templateFile.text();

  await axios
    .post(
      "/cuserv/v1/templates/import",
      {
        template_data: btoa(unescape(encodeURIComponent(templateFileContents))),
      },
      {
        errorContext: "Failed to import template",
        loading,
      },
    )
    .then((response) => {
      serviceTemplatesStore.addServiceTemplateByUuid(response.data.uuid);
    });

  toast("Imported template");
}
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
