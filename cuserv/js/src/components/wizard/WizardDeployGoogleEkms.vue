<template>
  <WizardBreadContainer :crumbs="wizardCrumbs" :page-index="state.pageIndex" />

  <component
    :is="wizardPages[state.pageIndex].component"
    v-model:serviceName="state.serviceName"
    v-model:serviceCategory="state.serviceCategory"
    v-model:serviceAccess="state.serviceAccess"
    v-model:serviceAccounts="state.serviceAccounts"
    :service-uuid="state.serviceUuid"
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
import WizardFinish from "@/components/wizard/WizardFinish.vue";
import WizardGeneralInfo from "@/components/wizard/WizardGeneralInfo.vue";
import WizardGoogleEkmsInfo from "@/components/wizard/WizardGoogleEkmsInfo.vue";
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

  serviceAccounts: [],
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
    component: WizardGoogleEkmsInfo,
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
    template_uuid: templateData.value?.objInfo.uuid,
    service_name: state.serviceName,
    category: state.serviceCategory,
    access_control: {
      grant_identities: [],
      grant_roles: [],
    },
    params: {
      "@type": "fx/rkproto.cuserv.DeployGoogleEkmsParams",
      accounts: [],
      device_address: location.host,
    },
  };

  for (const access of state.serviceAccess) {
    if (access.type === "Role") {
      body.access_control.grant_roles.push(access.uuid);
    } else if (access.type === "Identity") {
      body.access_control.grant_identities.push(access.uuid);
    }
  }

  // remove empty strings
  body.params.accounts = state.serviceAccounts.filter((x) => x);

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
