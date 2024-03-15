<template>
  <DeployedServiceWrapper :crumbs="crumbs" :loading="loading">
    <InformationAndActions
      :description="serviceDescription"
      :table-items="[
        ['Name', state.serviceName],
        ['Type', state.templateName],
        ['Category', state.serviceCategory],
        ['Created', state.serviceCreation],
      ]"
      :title="state.serviceName"
    >
      <template #actions>
        <DeployedServiceEdit
          :category="state.serviceCategory"
          :name="state.serviceName"
          :uuid="props.serviceUuid"
        />
        <DeployedServiceDelete
          :uuid="props.serviceUuid"
          @finished="$router.replace(crumbs[crumbs.length - 2].to)"
        />
      </template>

      <RouterLink
        v-for="link in serviceLinks"
        :key="link.to"
        :to="link.to"
        class="deployed-service-main__actions-link"
      >
        <img class="deployed-service-main__actions-img" :src="link.imgSrc" />
        {{ link.text }}
      </RouterLink>
    </InformationAndActions>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import {
  computed,
  defineProps,
  provide,
  reactive,
  ref,
  watchEffect,
} from "vue";
import { useRoute } from "vue-router";

import { useBus } from "$shared/bus.js";

import DeployedServiceDelete from "@/components/deploy-service/DeployedServiceDelete.vue";
import DeployedServiceEdit from "@/components/deploy-service/DeployedServiceEdit.vue";
import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";
import InformationAndActions from "@/components/InformationAndActions.vue";
import { timestampToDate } from "@/misc.js";

const route = useRoute();

const props = defineProps({
  serviceUuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);
const templateData = ref(false);
const serviceData = ref(false);

const state = reactive({
  serviceType: "",
  serviceName: "Service",
  serviceCategory: "",
  serviceCreation: "",
  templateName: "",
  templateUuid: "",

  associatedObjects: [],
});

provide("templateData", templateData);
provide("serviceData", serviceData);

const crumbs = computed(() => {
  return [
    {
      to: { name: "landing" },
      name: "Service Management",
    },
    {
      to: { name: "deployedServices" },
      name: "Deployed Services",
    },
    {
      to: {
        name: "deployedService",
        params: route.params,
      },
      name: state.serviceName,
    },
  ];
});

const serviceDescription = computed(() => {
  switch (state.serviceType) {
    case "ClientApplication":
      return `Futurex solutions integrate with a vast array of client applications. The broad integration possibilities give you more opportunities to protect sensitive data. Having deployed this client application, you may manage it via the objects below.\n\nSelect the below categories to display network endpoints, manage keys, view activity logs, and control user access.`;

    case "GoogleEkms":
      return `Futurex offers full integration with Google Cloud External Key Manager (EKM). Create, store, and manage keys in a separate environment from your encrypted data. Our FIPS 140-2 Level 3 validated key management solution enhances data privacy and maintains control over encryption keys.\n\nSelect the below functions to manage Cryptospaces, view activity logs, control access, and manage Google Cloud Service Accounts.`;

    case "GoogleCse":
      return `Futurex offers full integration with Google Client Side Encryption (CSE).\n\nSelect the below functions to manage Users, view activity logs, and control access.`;

    case "PedInjection":
      return "Futurex offers secure key injections for series of supported devices. Select the below categroies to start an injection session, view previous sessions, view audit logs and manage user access.";

    default:
      return "";
  }
});

const serviceLinkLogs = {
  to: {
    name: "deployedServiceLogs",
  },
  imgSrc: "/shared/static/folder-cloud.svg",
  text: "LOGS",
};

const serviceLinkInstructions = {
  to: {
    name: "deployedServiceInstructions",
  },
  imgSrc: "/shared/static/book.svg",
  text: "INSTRUCTIONS",
};

const serviceLinks = computed(() => {
  switch (state.serviceType) {
    case "ClientApplication":
      return [
        {
          to: {
            name: "endpoints",
          },
          imgSrc: "/shared/static/cloud-add.svg",
          text: "ENDPOINTS",
        },
        {
          to: {
            name: "clientAppKeys",
          },
          imgSrc: "/shared/static/key.svg",
          text: "KEYS",
        },
        serviceLinkLogs,
        serviceLinkInstructions,
      ];

    case "GoogleEkms":
      return [
        {
          to: {
            name: "cryptospaces",
          },
          imgSrc: "/shared/static/key.svg",
          text: "CRYPTOSPACES",
        },
        {
          to: {
            name: "serviceAccounts",
          },
          imgSrc: "/shared/static/cloud-add.svg",
          text: "SERVICE ACCOUNTS",
        },
        serviceLinkLogs,
        serviceLinkInstructions,
      ];

    case "GoogleCse":
      return [
        {
          to: {
            name: "googleUsers",
          },
          imgSrc: "/shared/static/cloud-add.svg",
          text: "USERS",
        },
        serviceLinkLogs,
        serviceLinkInstructions,
      ];

    case "PedInjection":
      return [
        {
          to: {
            name: "selectOptionalKeys",
          },
          imgSrc: "/shared/static/key.svg",
          text: "INJECT",
        },
        {
          to: {
            name: "manageProtocolOptions",
          },
          imgSrc: "/shared/static/icons/service-manager.svg",
          text: "PROTOCOL OPTIONS",
        },
        {
          to: {
            name: "keyInjectionSessions",
          },
          imgSrc: "/shared/static/folder-cloud.svg",
          text: "INJECTION LOGS",
        },
        {
          to: {
            name: "manageKeySlots",
          },
          imgSrc: "/shared/static/key.svg",
          text: "KEY SLOTS",
        },
        serviceLinkLogs,
      ];

    default:
      return [];
  }
});

function fetchTemplate() {
  axios
    .get(`/cuserv/v1/templates/${state.templateUuid}`, {
      errorContext: "Failed to fetch service template",
      loading,
    })
    .then((response) => {
      templateData.value = response.data;
    });
}

function fetchResults() {
  axios
    .get(`/cuserv/v1/services/${props.serviceUuid}`, {
      errorContext: "Failed to fetch service",
      loading,
    })
    .then((response) => {
      serviceData.value = response.data;

      state.serviceType = response.data.type;
      state.serviceName = response.data.objInfo.name;
      state.serviceCategory = response.data.category;
      state.serviceCreation = timestampToDate(
        response.data.objInfo.creationDate,
      );
      state.templateName = response.data.relatedInfo.templateName;
      state.templateUuid = response.data.templateUuid;
      state.associatedObjects = response.data.relatedInfo["associatedObjects"];

      fetchTemplate();
    });
}

watchEffect(fetchResults);
useBus("updateDeployedServices", fetchResults);
</script>
