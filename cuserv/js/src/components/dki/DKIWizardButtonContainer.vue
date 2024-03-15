<template>
  <!-- Hide the container if we are at the last page. -->
  <!-- The last page should be the finish page. -->
  <div
    v-if="pageIndex <= props.wizardPagesLength - 1"
    class="wizard-button-container"
  >
    <button v-if="pageIndex > 0" class="button-secondary" @click="pageIndex--">
      PREVIOUS
    </button>
    <!-- div is only for justify-content: space-between 🤷 -->
    <div v-else />

    <LoadingSpinner :loading="props.loading" />
    <button
      v-if="pageIndex === props.wizardPagesLength - 1"
      class="button-primary"
      :disabled="loading"
      @click="emit('deploy')"
    >
      INJECT
    </button>
    <button v-else class="button-primary" @click="emit('next')">NEXT</button>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

const emit = defineEmits(["update:pageIndex", "deploy", "next"]);

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
