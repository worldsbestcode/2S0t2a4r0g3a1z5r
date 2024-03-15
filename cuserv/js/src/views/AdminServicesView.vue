<template>
  <LoadingSpinner v-if="loading" :loading="loading" />
  <div v-else class="category-services-container">
    <nav>
      <RouterLink
        v-if="favoriteServices.length > 0"
        style="text-decoration: none"
        :to="{
          name: 'adminServiceCategory',
          params: { adminServiceCategory: 'preferred' },
        }"
      >
        <CategoryButton
          :active="route.params.adminServiceCategory === 'preferred'"
        >
          Preferred
        </CategoryButton>
      </RouterLink>

      <RouterLink
        v-if="recentServices.length > 0"
        style="text-decoration: none"
        :to="{
          name: 'adminServiceCategory',
          params: { adminServiceCategory: 'recent' },
        }"
      >
        <CategoryButton
          :active="route.params.adminServiceCategory === 'recent'"
        >
          Recent
        </CategoryButton>
      </RouterLink>

      <RouterLink
        v-for="category in categories"
        :key="category.name"
        style="text-decoration: none"
        :to="{
          name: 'adminServiceCategory',
          params: { adminServiceCategory: category.name },
        }"
      >
        <CategoryButton
          :active="route.params.adminServiceCategory === category.name"
        >
          {{ category.name }}
        </CategoryButton>
      </RouterLink>
    </nav>

    <div class="category-services-seperator" />

    <div class="services-container">
      <ServicesSearch v-model="state.search" />
      <template v-if="results?.length === 0">
        <div class="no-services-text">No services found</div>
      </template>
      <div
        v-else
        class="item-category__container"
        style="padding: 2rem"
        :class="props.listStyle === 'list' && 'item-category__container--list'"
      >
        <BaseService
          is="a"
          v-for="service in results"
          :key="service.name"
          :href="service.url"
          :name="service.name"
          :description="service.description"
          :img-src="service.icon"
          @click="serviceLinkClicked(service)"
        >
          <BaseServiceAction
            is="button"
            no-arrow
            @click.prevent="favoriteClicked(service)"
          >
            {{ isFavorited(service) ? "Unprefer" : "Prefer" }}
          </BaseServiceAction>
        </BaseService>
      </div>
    </div>
  </div>
</template>

<script setup>
import Fuse from "fuse.js";
import { computed, defineProps, reactive, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";
import { listStyle as listStyleProp } from "$shared/props.js";

import BaseService from "@/components/BaseService.vue";
import BaseServiceAction from "@/components/BaseServiceAction.vue";
import CategoryButton from "@/components/CategoryButton.vue";
import ServicesSearch from "@/components/ServicesSearch.vue";
import { useAdminServicesStore } from "@/store/admin-services";

const fuseOptions = {
  includeMatches: true,
  ignoreLocation: true,
  threshold: 0.4,
  keys: [
    {
      name: "name",
      weight: 2,
    },
    "description",
  ],
};

const fuse = new Fuse([], fuseOptions);

const route = useRoute();
const router = useRouter();
const store = useStore();
const adminServicesStore = useAdminServicesStore();

const props = defineProps({
  listStyle: listStyleProp,
});

const state = reactive({
  search: "",
});

const loading = computed(() => adminServicesStore.loading);
const categories = computed(() => adminServicesStore.categories);
const activeCategory = computed(() => route.params.adminServiceCategory);

const categoryServices = computed(() => {
  if (activeCategory.value === "preferred") {
    return favoriteServices.value;
  } else if (activeCategory.value === "recent") {
    return recentServices.value;
  } else {
    return categories.value.find((x) => x.name === activeCategory.value)
      ?.services;
  }
});

const results = computed(() => {
  if (state.search) {
    return fuse.search(state.search).map((x) => x.item);
  } else {
    return categoryServices.value;
  }
});

function mapServiceNamesToService(serviceNames) {
  const mappedServices = [];
  for (const serviceName of serviceNames) {
    const service = adminServicesStore.services.find(
      (x) => x.name === serviceName,
    );
    if (service) {
      mappedServices.push(service);
    }
  }

  return mappedServices;
}

const recentServices = computed(() =>
  mapServiceNamesToService(store.getters["profiles/recentServices"]),
);
const favoriteServices = computed(() =>
  mapServiceNamesToService(store.getters["profiles/favoriteServices"]),
);

function serviceLinkClicked(service) {
  store.dispatch("profiles/visit", service.name);
}

function favoriteClicked(service) {
  store.dispatch("profiles/favorite", service.name);
}

function isFavorited(service) {
  return favoriteServices.value?.includes(service);
}

function sendToBestCategory() {
  if (favoriteServices.value.length > 0) {
    router.replace({
      name: "adminServiceCategory",
      params: { adminServiceCategory: "preferred" },
    });
  } else if (recentServices.value.length > 0) {
    router.replace({
      name: "adminServiceCategory",
      params: { adminServiceCategory: "recent" },
    });
  } else {
    router.replace({
      name: "adminServiceCategory",
      params: { adminServiceCategory: categories.value[0].name },
    });
  }
}

watchEffect(() => {
  // handles edge case of removing the last favorited service and ending up in a "deadzone"
  if (categoryServices.value?.length === 0 && !loading.value) {
    sendToBestCategory();
  }
});

watchEffect(() => {
  if (route.name === "adminServices" && !loading.value) {
    sendToBestCategory();
  }
});

watchEffect(() => {
  fuse.setCollection(categoryServices.value);
});
</script>
