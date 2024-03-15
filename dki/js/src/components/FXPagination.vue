<template>
  <fx-separator />
  <nav class="fx-pagination">
    <div class="fx-pagination__pages">
      <fx-button
        icon="mdi-chevron-left"
        :disabled="page === 1"
        @click="page--"
      />
      <fx-button
        icon="mdi-chevron-right"
        :disabled="page === totalPages"
        @click="page++"
      />
    </div>
    <div class="fx-pagination__results">
      <fx-label class="mr-2" text="Display" theme="primary" />
      <!-- TODO <fx-combobox /> -->
      <select v-model.number="pageSize" class="fx-combobox">
        <option>5</option>
        <option>10</option>
        <option>15</option>
      </select>
    </div>
  </nav>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

const props = defineProps({
  page: {
    type: Number,
    required: true,
  },
  pageSize: {
    type: Number,
    required: true,
  },
  totalPages: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["update:page", "update:pageSize"]);

const page = computed({
  get() {
    return props.page;
  },
  set(value) {
    emit("update:page", value);
  },
});

const pageSize = computed({
  get() {
    return props.pageSize;
  },
  set(value) {
    emit("update:pageSize", value);
  },
});
</script>

<style scoped>
.fx-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.fx-pagination__pages {
  display: flex;
}

.fx-pagination__results {
  display: flex;
  align-items: center;
}

.fx-combobox {
  appearance: menulist;
  border: 1px solid var(--border-color);
  border-radius: 5px;
  height: 40px;
  min-width: fit-content;
  padding: 0 1rem;
}
</style>
