<template>
  <nav class="chc-pagination">
    <div class="chc-pagination__buttons">
      <button
        class="chc-pagination__button"
        :disabled="page === 1"
        @click="page--"
      >
        <span class="material-symbols-outlined">chevron_left</span>
      </button>

      <template v-for="(paginationPage, index) in paginationPages" :key="index">
        <div
          v-if="paginationPage === '...'"
          class="chc-pagination__button"
          style="pointer-events: none; border: 0"
        >
          ...
        </div>

        <button
          v-else
          class="chc-pagination__button"
          :class="page === paginationPage && 'chc-pagination__button--active'"
          @click="page = paginationPage"
        >
          {{ paginationPage }}
        </button>
      </template>

      <button
        class="chc-pagination__button"
        :disabled="page === totalPages"
        @click="page++"
      >
        <span class="material-symbols-outlined">chevron_right</span>
      </button>
    </div>

    <div>
      Display
      <select
        v-model.number="pageSize"
        class="chc-pagination__button"
        style="padding: 0 1rem; width: fit-content"
      >
        <option>5</option>
        <option>10</option>
        <option>15</option>
      </select>
      results
    </div>
  </nav>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

const emit = defineEmits([
  "update:page",
  "update:totalPages",
  "update:pageSize",
]);

const props = defineProps({
  page: {
    type: Number,
    default: 1,
  },
  totalPages: {
    type: Number,
    required: true,
  },
  pageSize: {
    type: Number,
    default: 5,
  },
});

const page = computed({
  get() {
    return props.page;
  },
  set(value) {
    emit("update:page", value);
  },
});
const totalPages = computed({
  get() {
    return props.totalPages;
  },
  set(value) {
    emit("update:totalPages", value);
  },
});
const pageSize = computed({
  get() {
    return props.pageSize;
  },
  set(value) {
    emit("update:page", 1);
    emit("update:pageSize", value);
  },
});

const paginationPages = computed(() =>
  paginate({ currentPage: page.value, totalPages: totalPages.value })
);

// Adapted from: https://www.zacfukuda.com/blog/pagination-algorithm
function paginate({ currentPage, totalPages }) {
  let items = [1];

  if (currentPage === 1 && totalPages === 1) {
    return items;
  }

  if (currentPage > 4) {
    items.push("...");
  }

  let r = 2;
  let r1 = currentPage - r;
  let r2 = currentPage + r;

  const start = r1 > 2 ? r1 : 2;
  const end = Math.min(totalPages, r2);

  for (let i = start; i <= end; i++) {
    items.push(i);
  }

  if (r2 + 1 < totalPages) {
    items.push("...");
  }

  if (r2 < totalPages) {
    items.push(totalPages);
  }

  return items;
}
</script>

<style scoped>
.chc-pagination {
  margin-top: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.chc-pagination__buttons {
  display: flex;
  gap: 0.25rem;
}

.chc-pagination__button {
  background: var(--secondary-background-color);
  border: 1px solid var(--border-color);
  border-radius: 5px;
  height: 40px;
  width: 40px;
  padding: 0;

  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.chc-pagination__button:disabled {
  pointer-events: none;
  opacity: 0.5;
}

.chc-pagination__button:hover {
  color: var(--primary-color);
  border-color: currentColor;
}

.chc-pagination__button:active {
  background: var(--primary-color);
  color: var(--primary-background-color);
  /* todo: Create variable for primary-color-border */
  border-color: #731313;
}

.chc-pagination__button--active {
  border-color: var(--primary-text-color);
  pointer-events: none;
}
</style>
