<template>
  <WizardPage
    :title="props.title"
    :loading="props.loading"
    style="margin-top: 2rem"
  >
    <slot />
  </WizardPage>

  <TaskWizardPageFooter :loading="props.loading" @click="emit('finish')">
    <template #footer>
      <slot name="footer" />
    </template>
  </TaskWizardPageFooter>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";

import WizardPage from "$shared/components/wizard/WizardPage.vue";

import TaskWizardPageFooter from "@/components/TaskWizardPageFooter.vue";

const emit = defineEmits(["finish"]);

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  loading: {
    type: Boolean,
  },
});
</script>
