<template>
  <WizardBreadContainer :crumbs="wizardCrumbs" :page-index="state.pageIndex" />

  <component
    :is="wizardPages[state.pageIndex].component"
    v-model:serviceName="state.serviceName"
    v-model:serviceCategory="state.serviceCategory"
    v-model:serviceAccess="state.serviceAccess"
    v-model:serviceGoogleCseIdpType="state.idpType"
    v-model:serviceGoogleCseAuthMechUuid="state.authMechUuid"
    v-model:serviceGoogleCseOidcUrl="state.oidcUrl"
    v-model:serviceGoogleCseOidcTlsCa="state.oidcTlsCa"
    v-model:serviceGoogleCseRotationPeriod="state.rotationPeriod"
    v-model:serviceGoogleCseEmailSuffix="state.emailSuffix"
    v-model:serviceGoogleCseDefaultWhitelisted="state.defaultWhitelisted"
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
import WizardGoogleCseInfo from "@/components/wizard/WizardGoogleCseInfo.vue";
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

  idpType: "OpenID Connect",
  rotationPeriod: "1 Month",
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
    component: WizardGoogleCseInfo,
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
      "@type": "fx/rkproto.cuserv.DeployGoogleCseParams",
      rotation_period: state.rotationPeriod,
      address: state.emailSuffix,
      default_access: state.defaultWhitelisted,
    },
  };

  for (const access of state.serviceAccess) {
    if (access.type === "Role") {
      body.access_control.grant_roles.push(access.uuid);
    } else if (access.type === "Identity") {
      body.access_control.grant_identities.push(access.uuid);
    }
  }

  if (state.idpType === "Existing") {
    body.params.authmech_uuid = state.authMechUuid;
  } else if (state.idpType === "OpenID Connect") {
    body.params.oidc_url = state.oidcUrl;
    body.params.oidc_pki = state.oidcTlsCa;
  } else if (state.idpType === "VirtuCrypt VIP") {
    body.params.virtucrypt_vip = true;
  } else if (state.idpType === "VirtuCrypt Test") {
    body.params.virtucrypt_vip = true;
    body.params.virtucrypt_test = true;
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
