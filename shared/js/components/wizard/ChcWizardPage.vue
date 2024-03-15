<template>
  <h1>{{ props.title }}</h1>
  <p>{{ props.description }}</p>

  <slot />
</template>

<script setup>
import { defineProps, inject, onMounted, onUnmounted } from "vue";

const addPage = inject("addPage");
const removePage = inject("removePage");

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: "",
  },
});

onMounted(() => {
  addPage(props);
});

onUnmounted(() => {
  removePage(props);
});
</script>
