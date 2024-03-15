<template>
  <LoadingSpinner v-if="loading" :loading="loading" />
  <div
    v-else-if="serviceTemplateCategories.length === 0"
    class="no-services-text"
  >
    No services available. Get started by importing templates.
  </div>
  <div v-else class="category-services-container">
    <nav>
      <RouterLink
        v-for="serviceTemplateCategory in serviceTemplateCategories"
        :key="serviceTemplateCategory"
        style="text-decoration: none"
        :to="{
          name: 'serviceTemplateCategory',
          params: { serviceTemplateCategory },
        }"
      >
        <CategoryButton :active="categoryButtonActive(serviceTemplateCategory)">
          {{ serviceTemplateCategory }}
        </CategoryButton>
      </RouterLink>
    </nav>

    <div class="category-services-seperator" />

    <div class="services-container">
      <ServicesSearch ref="servicesSearchRef" v-model="state.search" />

      <div v-if="serviceTemplatesToShow.length === 0" class="no-services-text">
        No services found
      </div>
      <div
        v-else
        class="item-category__container"
        :class="props.listStyle === 'list' && 'item-category__container--list'"
        style="padding: 2rem"
      >
        <BaseService
          :is="RouterLink"
          v-for="result in serviceTemplatesToShow"
          :key="result.objInfo.uuid"
          :to="{
            name: 'serviceTemplate',
            params: {
              serviceTemplateUuid: result.objInfo.uuid,
            },
          }"
          :img-src="result.params.details.icon"
          :name="result.objInfo.name"
          :description="result.params.details.vendor"
        >
          <BaseServiceAction
            :is="RouterLink"
            :to="{
              name: 'deploy',
              params: {
                serviceTemplateUuid: result.objInfo.uuid,
              },
            }"
          >
            Deploy
          </BaseServiceAction>
        </BaseService>
      </div>

      <div v-if="showSearchForMore" style="padding: 0 2rem">
        <ChcButton @click="scrollToSearch">Search for more...</ChcButton>
      </div>
    </div>
  </div>

  <RouterView />
</template>

<script setup>
import Fuse from "fuse.js";
import { computed, defineProps, reactive, ref, watchEffect } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import ChcButton from "$shared/components/ChcButton.vue";
import LoadingSpinner from "$shared/components/LoadingSpinner.vue";
import { listStyle as listStyleProp } from "$shared/props.js";

import BaseService from "@/components/BaseService.vue";
import BaseServiceAction from "@/components/BaseServiceAction.vue";
import CategoryButton from "@/components/CategoryButton.vue";
import ServicesSearch from "@/components/ServicesSearch.vue";
import { useServiceTemplatesStore } from "@/store/service-templates";

const fuseOptions = {
  includeMatches: true,
  ignoreLocation: true,
  threshold: 0.3,
  keys: ["objInfo.name", "params.details.vendor"],
};
const fuse = new Fuse([], fuseOptions);

const route = useRoute();
const router = useRouter();
const serviceTemplatesStore = useServiceTemplatesStore();

const props = defineProps({
  listStyle: listStyleProp,
});

const servicesSearchRef = ref();

const state = reactive({
  search: "",
});

const loading = computed(() => serviceTemplatesStore.loading);
const allServiceTemplates = computed(() => serviceTemplatesStore.all);
const serviceTemplatesByCategory = computed(
  () => serviceTemplatesStore.byCategory,
);

const serviceTemplateCategories = computed(() =>
  Object.keys(serviceTemplatesByCategory.value),
);

const activeServiceTemplateCategory = computed({
  get() {
    return route.params.serviceTemplateCategory;
  },
  set(value) {
    router.replace({
      name: "serviceTemplateCategory",
      params: { serviceTemplateCategory: value },
    });
  },
});

const activeServiceTemplates = computed(
  () => serviceTemplatesByCategory.value[activeServiceTemplateCategory.value],
);

const serviceTemplatesToShow = computed(() => {
  let results;
  if (state.search) {
    results = fuse.search(state.search).map((x) => x.item);
  } else {
    results = activeServiceTemplates.value;
  }
  return results ?? [];
});

const showSearchForMore = computed(
  () => activeServiceTemplateCategory.value === "Home" && !state.search,
);

function categoryButtonActive(serviceTemplateCategory) {
  return (
    activeServiceTemplateCategory.value === serviceTemplateCategory &&
    !state.search
  );
}

function scrollToSearch() {
  const searchInput = servicesSearchRef.value.input;
  searchInput.focus();
}

watchEffect(() => {
  fuse.setCollection(allServiceTemplates.value);
});

watchEffect(() => {
  if (serviceTemplateCategories.value.length === 0) {
    return;
  }

  let sendToFirstCategory = false;

  if (route.name === "serviceTemplates") {
    sendToFirstCategory = !activeServiceTemplateCategory.value;
  } else if (route.name === "serviceTemplateCategory") {
    const activeCategoryNotFound = !serviceTemplateCategories.value.includes(
      activeServiceTemplateCategory.value,
    );
    sendToFirstCategory = activeCategoryNotFound;
  }

  if (sendToFirstCategory) {
    activeServiceTemplateCategory.value = serviceTemplateCategories.value[0];
  }
});
</script>
