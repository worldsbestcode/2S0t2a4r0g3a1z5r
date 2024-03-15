<template>
  {{ state.pages }}
  <slot />
</template>

<script setup>
import { provide, reactive } from "vue";

const state = reactive({
  pages: [],
});

function addPage(pageInformation) {
  state.pages.push(pageInformation);
}

function removePage(pageInformation) {
  const pageInformationIndex = state.pages.indexOf(pageInformation);
  if (pageInformationIndex !== -1) {
    state.pages.splice(pageInformationIndex, 1);
  }
}

provide("addPage", addPage);
provide("removePage", removePage);
</script>
