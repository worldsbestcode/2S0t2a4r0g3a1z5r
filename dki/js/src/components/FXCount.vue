<template>
  <div class="fx-count-container">
    <fx-label class="mr-2" :text="title" />
    <v-avatar color="var(--primary-color)" size="26">
      <span class="count">{{ count }}</span>
    </v-avatar>
  </div>
</template>

<script setup>
import { defineProps } from "vue";
defineProps({
  title: {
    type: String,
    default: "",
  },
  count: {
    type: Number,
    default: 0,
  },
});
</script>

<style scoped>
.fx-count-container {
  display: flex;
  align-items: center;
  width: fit-content;
}
.count {
  font-size: 12px;
  font-weight: bold;
  color: var(--primary-background-color);
}
</style>
