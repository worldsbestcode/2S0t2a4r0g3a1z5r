<template>
  <WizardBreadContainer :crumbs="wizardCrumbs" :page-index="state.pageIndex" />

  <component
    :is="state.wizardPages[state.pageIndex].component"
    v-model:serviceAccess="state.serviceAccess"
    v-model:serviceCategory="state.serviceCategory"
    v-model:serviceName="state.serviceName"
    v-model:existingKeys="state.existingKeys"
    v-model:servicePedInjectDevices="state.devices"
    v-model:servicePedInjectGeneralInfo="state.deviceGroupName"
    v-model:servicePedInjectKeyInfo="state.keyInfo"
    v-model:servicePedInjectProtocolInfo="state.servicePedInjectProtocolInfo"
    :service-uuid="state.serviceUuid"
    :template-uuid="templateUuid"
  />

  <WizardButtonContainer
    v-model:pageIndex="state.pageIndex"
    :wizard-pages-length="state.wizardPages.length"
    @deploy="deployService"
  />
</template>

<script setup>
import axios from "axios";
import { computed, inject, onBeforeMount, reactive } from "vue";

import DKIWizardKeys from "@/components/dki/DKIWizardKeys.vue";
import WizardAccess from "@/components/wizard/WizardAccess.vue";
import WizardBreadContainer from "@/components/wizard/WizardBreadContainer.vue";
import WizardButtonContainer from "@/components/wizard/WizardButtonContainer.vue";
import WizardFinish from "@/components/wizard/WizardFinish.vue";
import WizardGeneralInfo from "@/components/wizard/WizardGeneralInfo.vue";
import { useDeployedServicesStore } from "@/store/deployed-services";

const deployedServicesStore = useDeployedServicesStore();

const templateData = inject("templateData");

const state = reactive({
  pageIndex: 0,
  serviceName: templateData.value.objInfo.name,
  serviceCategory: templateData.value?.params?.details?.categories[0] ?? "",
  serviceAccess: [],
  serviceUuid: "",
  existingKeys: [],
  wizardPages: [],
});

const templateUuid = computed(() => templateData.value?.objInfo.uuid);

state.wizardPages = [
  {
    name: "General Info",
    component: WizardGeneralInfo,
  },
  {
    name: "Who Has Access?",
    component: WizardAccess,
  },
  {
    name: "Finish",
    component: WizardFinish,
  },
];

const wizardCrumbs = computed(() => {
  return state.wizardPages.map((x) => x.name);
});

function deployService() {
  const body = {
    template_uuid: templateUuid.value,
    service_name: state.serviceName,
    category: state.serviceCategory,
    access_control: {
      grant_identities: [],
      grant_roles: [],
    },
    params: {
      "@type": "fx/rkproto.cuserv.DeployPedInjectParams",
      keys: [],
    },
  };

  for (const access of state.serviceAccess) {
    if (access.type === "Role") {
      body.access_control.grant_roles.push(access.uuid);
    } else if (access.type === "Identity") {
      body.access_control.grant_identities.push(access.uuid);
    }
  }

  state.existingKeys.forEach((key) => {
    body.params.keys.push({
      uuid: key.uuid,
      templateName: key.tag,
    });
  });

  axios
    .post("/cuserv/v1/services/deploy", body, {
      errorContext: "Failed to deploy service",
    })
    .then((response) => {
      const serviceUuid = response.data.result.objInfo.uuid;
      state.serviceUuid = serviceUuid;
      state.pageIndex++;

      deployedServicesStore.addServiceByUuid(serviceUuid);
    });
}

onBeforeMount(() => {
  axios
    .get(`/cuserv/v1/templates/${templateUuid.value}`, {
      errorContext: "Failed to fetch template details",
    })
    .then((response) => {
      let keys = [];
      if (response.status === 200) {
        response.data.params.keys.forEach((key) => {
          if (key.origin === "Existing") {
            keys.push(key);
          }
        });
      }

      if (keys.length > 0) {
        state.wizardPages.splice(2, 0, {
          name: "Select existing keys",
          component: DKIWizardKeys,
        });
      }
    });
});
</script>
