<template>
  <div class="cover-screen cover-screen-service-template">
    <RouterBreadCrumbs seperator :crumbs="crumbs" main-padding />

    <div class="available-services-content chc-main-horizontal-padding">
      <div class="available-services-content__left">
        <header class="available-services-header">
          <img
            v-if="state.icon"
            class="available-services-header__icon"
            :src="state.icon"
          />
          <div class="available-services-header__text" :title="state.name">
            {{ state.name }}
          </div>
          <LoadingSpinner :loading="loading" />
        </header>

        <div class="available-services-description">
          <header class="available-services-description__header">
            Description
          </header>
          <div class="available-services-description__text">
            <CuservMarkdown :markdown="state.description" />
            <CuservMarkdown :markdown="state.details" />
          </div>
        </div>

        <div
          v-if="state.learnMore.length > 0"
          class="available-services-description"
        >
          <header class="available-services-description__header">
            Learn More
          </header>
          <div class="available-services-learn">
            <a
              v-for="learn in state.learnMore"
              :key="learn.title + learn.url"
              class="chc-link"
              :href="learn.url"
            >
              <div class="available-services-content__learn-img">
                <img :src="learn.icon" />
              </div>
              <div
                class="available-services-learn__header-text available-services-content__bolded"
              >
                {{ learn.title }}
              </div>
              <div class="available-services-learn__description">
                {{ learn.description }}
              </div>
            </a>
          </div>
        </div>
      </div>
      <div class="available-services-content__right">
        <div class="available-services-content__buttons">
          <RouterLink
            :to="{ name: 'deploy' }"
            class="button-primary button-link"
          >
            DEPLOY
          </RouterLink>
          <a
            :href="state.documentationUrl"
            class="button-secondary button-link"
          >
            DOCUMENTATION
          </a>
        </div>

        <div v-if="state.vendor" class="available-services-content__img-text">
          <img
            class="available-services-content__small-icon"
            src="/shared/static/courthouse.svg"
          />
          <div class="available-services-content__bolded">Company name</div>
          <div>{{ state.vendor }}</div>
        </div>

        <div
          v-if="state.vendorUrl"
          class="available-services-content__img-text"
        >
          <img
            class="available-services-content__small-icon"
            src="/shared/static/global.svg"
          />
          <div class="available-services-content__bolded">Company URL</div>
          <div>
            <a class="chc-link" :href="state.vendorUrl">{{
              state.vendorUrl
            }}</a>
          </div>
        </div>

        <template v-if="state.version">
          <div class="available-services-content__supported">
            Supported version
          </div>
          <div class="available-services-content__supported-stuff">
            <div class="available-services-content__bolded">Version</div>
            <div>{{ state.version }}</div>
          </div>
        </template>

        <div
          v-if="state.creationDate"
          class="available-services-content__supported-stuff"
        >
          <div class="available-services-content__bolded">Released on</div>
          <div>{{ state.creationDate }}</div>
        </div>
        <div
          v-if="state.modifyDate"
          class="available-services-content__supported-stuff"
        >
          <div class="available-services-content__bolded">Updated on</div>
          <div>{{ state.modifyDate }}</div>
        </div>

        <template v-if="state.resources.length > 0">
          <div class="available-services-content__resources">Resources</div>
          <div class="available-services-content__resources-links">
            <ul>
              <li
                v-for="resource in state.resources"
                :key="resource.title + resource.url"
              >
                <a class="chc-link" :href="resource.url">
                  {{ resource.title }}
                </a>
              </li>
            </ul>
          </div>
        </template>
      </div>
    </div>
  </div>

  <RouterView :crumbs="crumbs" :template-type="state.templateType" />
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, provide, reactive, ref } from "vue";
import { useRoute } from "vue-router";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";
import RouterBreadCrumbs from "$shared/components/RouterBreadCrumbs.vue";

import CuservMarkdown from "@/components/CuservMarkdown.vue";

const route = useRoute();

const props = defineProps({
  serviceTemplateUuid: {
    type: String,
    required: true,
  },
  serviceTemplateCategory: {
    type: String,
    required: true,
  },
});

const loading = ref(false);
const templateData = ref(null);

provide("templateData", templateData);

const state = reactive({
  name: "Template",
  creationDate: "",
  modifyDate: "",

  icon: "",
  description: "",
  details: "",

  vendor: "",
  vendorUrl: "",

  resources: [],
  learnMore: [],
  documentationUrl: "",
  version: "",
  templateType: "",
});

const crumbs = computed(() => {
  return [
    {
      to: { name: "landing" },
      name: "Service Management",
    },
    {
      to: { name: "serviceTemplates" },
      name: "Available Services",
    },
    {
      to: {
        name: "serviceTemplateCategory",
        params: {
          serviceTemplateCategory: props.serviceTemplateCategory,
        },
      },
      name: props.serviceTemplateCategory,
    },
    {
      to: {
        name: "serviceTemplate",
        params: route.params,
      },
      name: state.name,
    },
  ];
});

function timestampToDate(timestamp) {
  return new Date(parseInt(timestamp) * 1000).toLocaleDateString([], {
    dateStyle: "medium",
  });
}

axios
  .get(`/cuserv/v1/templates/${props.serviceTemplateUuid}`, {
    errorContext: "Failed to fetch service details",
    loading,
  })
  .then((response) => {
    const data = response.data;
    templateData.value = data;

    state.name = data.objInfo.name;
    state.creationDate = timestampToDate(data.objInfo.creationDate);
    state.modifyDate = timestampToDate(data.objInfo.modifyDate);

    state.icon = data.params.details.icon;
    state.description = data.params.details.description;
    state.details = data.params.details.details;

    state.vendor = data.params.details.vendor;
    state.vendorUrl = data.params.details.url;

    state.resources = data.params.details.resources;
    state.learnMore = data.params.details.learnMore;
    state.documentationUrl = data.params.details.documentationUrl;
    state.version = data.params.details?.versions?.join(", ");
    state.templateType = data.params.type;
  });
</script>

<style scoped>
.cover-screen-service-template {
  display: flex;
  flex-direction: column;
  padding-bottom: 0;
  /* overflow: initial; */
}

.cover-screen-service-template
  :deep(.available-services-bread__wrapper > .available-services-bread) {
  max-width: initial;
}

.available-services-content {
  flex-grow: 1;
  display: flex;
}

.available-services-content__left {
  flex-grow: 1;
  padding: 2rem;
  padding-left: 0;
  overflow: hidden;
}

.available-services-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.available-services-header__text {
  font-weight: 900;
  font-size: 48px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.available-services-description {
  margin-bottom: 2rem;
}

.available-services-description:last-child {
  margin-bottom: 1rem;
}

.available-services-description__header {
  font-weight: 700;
  font-size: 18px;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.available-services-description__text {
  margin-top: 1rem;
  color: var(--secondary-text-color);
}

.available-services-learn {
  margin-top: 1.5rem;
  display: grid;
  justify-content: center;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}

.available-services-learn__header-text {
  margin-top: 1rem;
  text-align: center;
}

.available-services-content__learn-img {
  padding: 2rem;
  background: var(--secondary-background-color);
  border-radius: 5px;
  border: 1px solid var(--border-color);
  display: flex;
}

.available-services-content__learn-img img {
  width: 100%;
}

.available-services-learn__description {
  color: var(--secondary-text-color);
}

.available-services-content__right {
  flex: 0 0 max-content;
  padding: 2rem;
  background: var(--secondary-background-color);

  transition: margin 1s;
  margin-right: calc(var(--main-padding) * -1);
}

.available-services-content__buttons {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 4rem;
}

.available-services-content__deploy,
.available-services-content__documentation {
  height: 50px;
  border-radius: 5px;
  font-weight: 500;

  width: 300px;
  text-decoration: none;

  display: flex;
  align-items: center;
  justify-content: center;
}

.available-services-content__deploy {
  color: var(--primary-background-color);
  background: var(--primary-color);
}

.available-services-content__documentation {
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.available-services-content__icon-text {
  display: flex;
  align-items: center;
  font-weight: 700;
  gap: 0.5rem;
}

.available-services-content__small-icon {
  height: 1.5rem;
  width: 1.5rem;
}

.available-services-content__img-text {
  display: grid;
  grid-template-columns: max-content 1fr;
  column-gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.available-services-content__img-text :nth-child(3) {
  grid-column: 2;
}

.available-services-content__bolded {
  font-weight: 700;
}

.available-services-content__supported-stuff {
  margin-bottom: 1rem;
}

.available-services-content__supported {
  font-weight: 700;
  font-size: 18px;
  margin-top: 3rem;
  margin-bottom: 0.75rem;
}

.available-services-content__resources {
  font-weight: 700;
  font-size: 18px;
  margin-top: 3rem;
  margin-bottom: 0.75rem;
}

.available-services-content__resources-links ul {
  padding-left: 1rem;
}
</style>
