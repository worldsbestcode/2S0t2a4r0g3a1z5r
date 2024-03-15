<template>
  <div v-if="props.loading" class="shared-spinning-border" />
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  loading: {
    type: Boolean,
  },
});
</script>
