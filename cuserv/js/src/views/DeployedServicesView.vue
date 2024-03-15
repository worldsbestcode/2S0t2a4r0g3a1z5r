<template>
  <LoadingSpinner v-if="loading" :loading="loading" />
  <div v-else-if="deployedServicesStore.services.length === 0" class="no-items">
    No deployed services. Get started by deploying a service in available
    services.
  </div>
  <template
    v-for="(services, category) in categoriesAndServices"
    v-else
    :key="category"
  >
    <div class="item-category">
      <div class="item-category__text" :title="category">{{ category }}</div>
      <div class="item-category__line" />
    </div>
    <div
      class="item-category__container"
      :class="props.listStyle === 'list' && 'item-category__container--list'"
    >
      <BaseService
        :is="RouterLink"
        v-for="result in services"
        :key="result.objInfo.uuid"
        :to="{
          name: 'deployedService',
          params: { serviceUuid: result.objInfo.uuid },
        }"
        :img-src="result.relatedInfo.templateIcon"
        :name="result.objInfo.name"
        :description="result.relatedInfo.templateName"
      >
        <!-- experimenting with "temporary variables in template" -->
        <template v-for="action in [quickAction(result)]" :key="action">
          <BaseServiceAction
            :is="action.is"
            v-if="action"
            v-bind="action.props"
          >
            {{ action.text }}
          </BaseServiceAction>
        </template>
      </BaseService>
    </div>
  </template>

  <RouterView />
</template>

<script setup>
import { computed, defineProps } from "vue";
import { RouterLink } from "vue-router";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";
import { listStyle as listStyleProp } from "$shared/props.js";

import BaseService from "@/components/BaseService.vue";
import BaseServiceAction from "@/components/BaseServiceAction.vue";
import { useDeployedServicesStore } from "@/store/deployed-services";

const deployedServicesStore = useDeployedServicesStore();

const props = defineProps({
  listStyle: listStyleProp,
});

const loading = computed(() => deployedServicesStore.loading);
const categoriesAndServices = computed(() => {
  const ret = {};
  for (const service of deployedServicesStore.services) {
    const category = service.category;
    if (ret[category]) {
      ret[category].push(service);
    } else {
      ret[category] = [service];
    }
  }

  return ret;
});

function quickAction(service) {
  const quickActions = {
    GoogleEkms: {
      is: RouterLink,
      props: {
        to: {
          name: "cryptospaces",
          params: { serviceUuid: service.objInfo.uuid },
        },
      },
      text: "CryptoSpaces",
    },
    ClientApplication: {
      is: RouterLink,
      props: {
        to: {
          name: "clientAppKeys",
          params: { serviceUuid: service.objInfo.uuid },
        },
      },
      text: "Keys",
    },
    GoogleCse: {
      is: RouterLink,
      props: {
        to: {
          name: "googleUsers",
          params: { serviceUuid: service.objInfo.uuid },
        },
      },
      text: "Users",
    },
    PedInjection: {
      is: RouterLink,
      props: {
        to: {
          name: "selectOptionalKeys",
          params: {
            serviceUuid: service.objInfo.uuid,
            serviceName: service.objInfo.name,
          },
        },
      },
      text: "Inject",
    },
  };

  return quickActions[service.type];
}
</script>
