<template>
  <WizardPage title="Service Info" :loading="loading">
    <ChcLabel label="Authentication Mechanisms" div>
      <template
        v-for="endpoint in props.templateEndpoints"
        :key="endpoint.name"
      >
        <div>
          Choose an authentication mechanism for the "{{ endpoint.name }}"
          endpoint.
        </div>

        <WizardClientAppInfoEndpoint
          v-model="authMechanismsForEndpoints[endpoint.name]"
          :auth-mechanisms="state.authMechanisms"
          :endpoint="endpoint"
        />
      </template>
    </ChcLabel>
  </WizardPage>
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, defineProps, reactive, ref } from "vue";

import ChcLabel from "$shared/components/ChcLabel.vue";
import WizardPage from "$shared/components/wizard/WizardPage.vue";

import WizardClientAppInfoEndpoint from "@/components/wizard/WizardClientAppInfoEndpoint.vue";

const emit = defineEmits(["update:serviceClientAppInfo"]);

const props = defineProps({
  templateEndpoints: {
    type: Array,
    required: true,
  },
  serviceClientAppInfo: {
    type: Object,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  authMechanisms: [],
  endpoints: [],
});

const authMechanismsForEndpoints = computed({
  get() {
    return props.serviceClientAppInfo;
  },
  set(value) {
    emit("update:serviceClientAppInfo", value);
  },
});

axios
  .get("/cuserv/v1/users/authmechs", {
    params: {
      page: 1,
      pageSize: 100,
    },
    errorContext: "Failed to fetch authentication mechanisms",
    loading,
  })
  .then((response) => {
    state.authMechanisms = response.data.results.filter(
      (x) => x.authType !== "Jwt",
    );
  });

for (const endpoint of props.templateEndpoints) {
  authMechanismsForEndpoints.value[endpoint.name] = {};
}
</script>

<style scoped>
.auth-type-container {
  display: grid;
  justify-content: center;
  gap: 0.75rem;
  margin: 1.5rem 0;
}
</style>
