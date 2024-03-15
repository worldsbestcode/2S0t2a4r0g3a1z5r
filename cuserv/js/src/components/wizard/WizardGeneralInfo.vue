<template>
  <WizardPage title="General Info">
    <ChcInput
      v-model="name"
      hint="length 3-64"
      label="Service Name"
      placeholder="Service name"
    />
    <DeployServiceCategoryFuzzy v-model="category" />
  </WizardPage>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcInput from "$shared/components/ChcInput.vue";
import WizardPage from "$shared/components/wizard/WizardPage.vue";

import DeployServiceCategoryFuzzy from "@/components/deploy-service/DeployServiceCategoryFuzzy.vue";

const emit = defineEmits(["update:serviceName", "update:serviceCategory"]);

const props = defineProps({
  serviceName: {
    type: String,
    required: true,
  },
  serviceCategory: {
    type: String,
    required: true,
  },
});

const name = computed({
  get() {
    return props.serviceName;
  },
  set(value) {
    emit("update:serviceName", value);
  },
});

const category = computed({
  get() {
    return props.serviceCategory;
  },
  set(value) {
    emit("update:serviceCategory", value);
  },
});
</script>

<style scoped>
.wizard-general-info-container {
  display: grid;
  gap: 2rem;
  width: fit-content;
  margin: auto;
}
</style>
