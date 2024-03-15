<template>
  <WizardBreadContainer :crumbs="wizardCrumbs" :page-index="state.pageIndex" />

  <component
    :is="wizardPages[state.pageIndex].component"
    v-model:serviceName="state.serviceName"
    v-model:serviceCategory="state.serviceCategory"
    v-model:serviceAccess="state.serviceAccess"
    v-model:serviceClientAppInfo="state.serviceClientAppInfo"
    :service-uuid="state.serviceUuid"
    :template-endpoints="templateData?.params?.endpoints"
  />

  <WizardButtonContainer
    v-model:pageIndex="state.pageIndex"
    :loading="loading"
    :wizard-pages-length="wizardPages.length"
    @deploy="deployService"
  />
</template>

<script setup>
import axios from "axios";
import { computed, inject, reactive, ref } from "vue";

import WizardAccess from "@/components/wizard/WizardAccess.vue";
import WizardBreadContainer from "@/components/wizard/WizardBreadContainer.vue";
import WizardButtonContainer from "@/components/wizard/WizardButtonContainer.vue";
import WizardClientAppInfo from "@/components/wizard/WizardClientAppInfo.vue";
import WizardFinish from "@/components/wizard/WizardFinish.vue";
import WizardGeneralInfo from "@/components/wizard/WizardGeneralInfo.vue";
import { useDeployedServicesStore } from "@/store/deployed-services";

const deployedServicesStore = useDeployedServicesStore();

const templateData = inject("templateData");

const loading = ref(false);

const state = reactive({
  pageIndex: 0,
  serviceName: templateData.value.objInfo.name,
  serviceCategory: templateData.value?.params?.details?.categories[0] ?? "",
  serviceAccess: [],
  serviceUuid: "",

  serviceClientAppInfo: {},
});

const wizardPages = [
  {
    name: "General Info",
    component: WizardGeneralInfo,
  },
  {
    name: "Who has Access?",
    component: WizardAccess,
  },
  {
    name: "Service Info",
    component: WizardClientAppInfo,
  },
  {
    name: "Finish",
    component: WizardFinish,
  },
];

const wizardCrumbs = computed(() => {
  return wizardPages.map((x) => x.name);
});

function deployService() {
  const body = {
    template_uuid: templateData.value?.objInfo?.uuid,
    service_name: state.serviceName,
    category: state.serviceCategory,
    access_control: {
      grant_identities: [],
      grant_roles: [],
    },
    params: {
      "@type": "fx/rkproto.cuserv.DeployClientAppParams",
      endpoints: [],
    },
  };

  for (const access of state.serviceAccess) {
    if (access.type === "Role") {
      body.access_control.grant_roles.push(access.uuid);
    } else if (access.type === "Identity") {
      body.access_control.grant_identities.push(access.uuid);
    }
  }

  for (const endpointName in state.serviceClientAppInfo) {
    const endpoint = state.serviceClientAppInfo[endpointName];

    const toPush = {
      endpoint: endpointName,
      auth_type: endpoint.type,
    };
    if (endpoint.uuid) {
      toPush.authmech_uuid = endpoint.uuid;
    }
    body.params.endpoints.push(toPush);
  }

  axios
    .post("/cuserv/v1/services/deploy", body, {
      errorContext: "Failed to deploy service",
      loading,
    })
    .then((response) => {
      const serviceUuid = response.data.result.objInfo.uuid;
      state.serviceUuid = serviceUuid;
      state.pageIndex++;

      deployedServicesStore.addServiceByUuid(serviceUuid);
    });
}
</script>
