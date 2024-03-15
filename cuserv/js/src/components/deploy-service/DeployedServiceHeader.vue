<template>
  <div class="deployed-service-header__wrapper">
    <header class="deployed-service-header">
      <img
        class="available-services-header__icon"
        style="margin-right: 1rem"
        :src="serviceData?.relatedInfo?.templateIcon"
      />
      <div style="overflow: hidden">
        <div
          class="deployed-service-header__service-name"
          :title="serviceData?.objInfo?.name"
        >
          {{ serviceData?.objInfo?.name }}
        </div>
        <div
          class="deployed-service-header__template-name"
          :title="serviceData?.relatedInfo?.templateName"
        >
          {{ serviceData?.relatedInfo?.templateName }}
        </div>
      </div>
    </header>
  </div>
  <RouterBreadCrumbs :crumbs="props.crumbs" />
</template>

<script setup>
import { defineProps, inject } from "vue";

import RouterBreadCrumbs from "$shared/components/RouterBreadCrumbs.vue";

const serviceData = inject("serviceData");

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
});
</script>

<style scoped>
.deployed-service-header__wrapper {
  background: var(--primary-background-color);
  border-bottom: 1px solid var(--border-color);
  padding: 0 2rem;
}

.deployed-service-header {
  height: 7rem;
  display: flex;
  align-items: center;
  max-width: 80rem;
  margin: auto;
}

.deployed-service-header__icon img {
  width: 100%;
  height: 100%;
}

.deployed-service-header__service-name {
  font-weight: 700;
  font-size: 22px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.deployed-service-header__template-name {
  font-size: 14px;
  color: var(--secondary-text-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
