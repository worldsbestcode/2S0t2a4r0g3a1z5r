<template>
  <DeployedServiceWrapper :crumbs="crumbs">
    <div class="deployed-service-main__wrapper">
      <div class="deployed-service-main">
        <div
          class="deployed-service-main__name"
          :title="`${serviceData?.objInfo?.name}` - Instructions"
        >
          {{ serviceData?.objInfo?.name }} - Instructions
        </div>
        <div class="instruction-categories">
          <button
            v-for="instructionCategory in state.instructionCategories"
            :key="instructionCategory"
            class="instruction-category"
            :class="
              state.selectedCategory === instructionCategory &&
              'instruction-category--active'
            "
            :title="instructionCategory"
            @click="state.selectedCategory = instructionCategory"
          >
            {{ instructionCategory }}
          </button>
        </div>

        <div
          v-if="state.selectedCategory"
          class="deployed-service-main__actions-text"
          style="margin-top: 2rem"
        >
          {{ state.selectedCategory }}
        </div>
        <LoadingSpinner :loading="loading" />
        <div v-if="state.instructions" class="instructions">
          <CuservMarkdown :markdown="state.instructions.setup" />
        </div>
      </div>
    </div>
  </DeployedServiceWrapper>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, inject, reactive, ref, watchEffect } from "vue";
import { useRoute } from "vue-router";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

import CuservMarkdown from "@/components/CuservMarkdown.vue";
import DeployedServiceWrapper from "@/components/deploy-service/DeployedServiceWrapper.vue";

const route = useRoute();

const serviceData = inject("serviceData");
const templateData = inject("templateData");

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  instructionCategories: [],
  selectedCategory: "",
  instructions: null,
});

const crumbs = computed(() => {
  return [
    ...props.crumbs,
    {
      to: {
        name: "deployedServiceInstructions",
        params: route.params,
      },
      name: "Instructions",
    },
  ];
});

const templateUuid = computed(() => templateData.value?.objInfo?.uuid);

async function fetchInstructionCategories() {
  // todo: parent route simply shouldn't render it's router view until it's done loading
  if (!templateUuid.value) {
    return;
  }

  await axios
    .get(`/cuserv/v1/templates/instructions/${templateUuid.value}`, {
      errorContext: "Failed to fetch instructions",
      loading,
    })
    .then((response) => {
      state.instructionCategories = response.data.setups;
    });
}

watchEffect(fetchInstructionCategories);

watchEffect(() => {
  state.selectedCategory = state.instructionCategories[0];
});

watchEffect(() => {
  if (state.selectedCategory) {
    axios
      .get(
        `/cuserv/v1/templates/instructions/${templateUuid.value}/${state.selectedCategory}`,
        {
          errorContext: `Failed to fetch instructions for "${state.selectedCategory}"`,
          loading,
        },
      )
      .then((response) => {
        state.instructions = response.data;
      });
  }
});
</script>

<style scoped>
.instruction-setup {
  color: var(--secondary-text-color);
  font-size: 14px;
  margin-top: 2rem;
}

.instruction-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.instruction-category {
  text-align: left;
  background: 0;
  border: 0;
  padding: 0;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.instruction-category--active,
.instruction-category:hover {
  text-decoration: underline;
}

.instructions {
  color: var(--secondary-text-color);
  font-size: 14px;
  margin-top: 2rem;
}
</style>
