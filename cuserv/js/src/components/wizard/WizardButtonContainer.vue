<template>
  <!-- Hide the container if we are at the last page. -->
  <!-- The last page should be the finish page. -->
  <WizardPageFooter v-if="pageIndex < props.wizardPagesLength - 1">
    <ChcButton v-if="pageIndex > 0" secondary @click="pageIndex--">
      PREVIOUS
    </ChcButton>

    <!-- div is only for justify-content: space-between 🤷 -->
    <div v-else />

    <ChcButton
      v-if="pageIndex === props.wizardPagesLength - 2"
      :loading="props.loading"
      @click="emit('deploy')"
    >
      DEPLOY
    </ChcButton>
    <ChcButton v-else @click="pageIndex++">NEXT</ChcButton>
  </WizardPageFooter>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import WizardPageFooter from "$shared/components/wizard/WizardPageFooter.vue";

const emit = defineEmits(["update:pageIndex", "deploy"]);

const props = defineProps({
  loading: {
    type: Boolean,
    required: true,
  },
  pageIndex: {
    type: Number,
    required: true,
  },
  wizardPagesLength: {
    type: Number,
    required: true,
  },
});

const pageIndex = computed({
  get() {
    return props.pageIndex;
  },
  set(value) {
    emit("update:pageIndex", value);
  },
});
</script>
