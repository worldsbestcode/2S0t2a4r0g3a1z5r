<template>
  <!-- todo: Add loading support to wizard fuzzy input -->
  <WizardFuzzyInput
    v-model:selected="category"
    :data="state.deployedServiceCategories"
    :display="(x) => x"
    hint="length 3-128"
    :keys="[]"
    label="Service Category"
    no-search-results="No categories found"
    placeholder="Service category"
    single
  />
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, defineProps, reactive, ref } from "vue";

import WizardFuzzyInput from "@/components/wizard/WizardFuzzyInput.vue";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  deployedServiceCategories: [],
});

const category = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit("update:modelValue", value);
  },
});

axios
  .get("/cuserv/v1/services/categories", {
    errorContext: "Failed to fetch categories",
    loading,
  })
  .then((response) => {
    state.deployedServiceCategories = response.data.categories;
  });
</script>
