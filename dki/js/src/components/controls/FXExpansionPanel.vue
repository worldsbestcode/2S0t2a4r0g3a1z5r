<template>
  <div class="fx-expansion-panel">
    <div class="fx-expansion-panel__header" @click="toggleContent">
      <slot name="fx-expansion-header"></slot>
      <v-icon
        v-if="!isOpen && !disableExpansion"
        class="fx-expansion-panel__icon"
      >
        mdi-chevron-down
      </v-icon>
      <v-icon v-else-if="!disableExpansion" class="fx-expansion-panel__icon">
        mdi-chevron-up
      </v-icon>
    </div>
    <fx-separator
      v-if="isOpen && !disableExpansion"
      length="98%"
      thickness="1.4px"
    />
    <div v-if="isOpen && !disableExpansion" class="fx-expansion-panel__content">
      <slot name="fx-expansion-content"> </slot>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref } from "vue";
const isOpen = ref(false);
const toggleContent = () => {
  isOpen.value = !isOpen.value;
};

defineProps({
  disableExpansion: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped>
.fx-expansion-panel {
  background-color: var(--primary-background-color);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  width: fill;
  height: fit-content;
}

.fx-expansion-panel__header {
  display: flex;
  cursor: pointer;
  align-items: center;
  min-height: 50px;
}
.fx-expansion-panel__icon {
  margin-left: auto;
  margin-right: 0.3rem;
  color: var(--primary-color);
}

.fx-expansion-panel__content {
  display: flex;
  align-items: center;
}
</style>
