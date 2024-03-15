<template>
  <nav class="chc-table-controls">
    <!-- Search box -->
    <div class="chc-table-controls__search-container" v-if="props.searching">
      <input
        v-model="searchTerm"
        class="chc-table-controls__search chc-input"
        placeholder="Search keyword"
      />
      <img
        class="chc-table-controls__search-icon"
        src="/shared/static/search-icon.svg"
      />
    </div>

    <!-- Buttons: slot=buttons -->
    <div class="chc-table-controls__buttons">
      <slot name="buttons"></slot>
    </div>
  </nav>

  <!-- Table data: slot=table -->
  <table class="chc-table">
    <slot name="table"></slot>
  </table>

  <!-- Pagination controls -->
  <nav class="chc-table-pagination" v-if="props.paging">
    <div>
      <button
        class="chc-table-pagination__button"
        :disabled="page <= 1"
        @click="page--"
      >
        &lt;
      </button>

      <button
        class="chc-table-pagination__button"
        v-for="pageNum in numberedButtons"
        :disabled="pageNum == page"
        @click="page = pageNum"
      >
        {{ pageNum }}
      </button>
      <button
        class="chc-table-pagination__button"
        :disabled="page >= totalPages"
        @click="page++"
      >
        &gt;
      </button>
    </div>
    <div v-if="props.hasArchive" @click="archive = !archive">
      <input type="checkbox" v-model="archive" />
      <span style="cursor: pointer"> Include archived </span>
    </div>
    <div>
      Display
      <select
        v-model.number="pageSize"
        class="chc-table-pagination__button"
        style="padding: 0 1rem; width: fit-content"
      >
        <option>5</option>
        <option>10</option>
        <option>25</option>
        <option>50</option>
      </select>
      results
    </div>
  </nav>
</template>

<script setup>
import {
  computed,
  defineEmits,
  defineProps,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";

import ChcCheckBox from "@/components/ChcCheckBox.vue";

const emit = defineEmits([
  "update:page",
  "update:totalPages",
  "update:pageSize",
  "update:search",
]);

const props = defineProps({
  search: {
    type: Boolean,
    default: true,
  },
  loading: {
    type: Boolean,
    required: true,
  },
  searching: {
    type: Boolean,
    default: true,
  },
  paging: {
    type: Boolean,
    default: true,
  },
  page: {
    type: Number,
    default: 1,
  },
  pageSize: {
    type: Number,
    default: 25,
  },
  totalPages: {
    type: Number,
    default: 1,
  },
  archive: {
    type: Boolean,
    default: false,
  },
  hasArchive: {
    type: Boolean,
    default: false,
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
    emit("update:pageSize", value);
  },
});
const archive = computed({
  get() {
    return props.archive;
  },
  set(value) {
    emit("update:archive", value);
  },
});

var searchTimeout = null;
const searchValue = ref("");
const searchTerm = computed({
  get() {
    return searchValue.value;
  },
  set(value) {
    searchValue.value = value;
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      searchTimeout = null;
      emit("update:search", searchValue.value);
    }, 300); // 300ms delay on emits
  },
});

const numberedButtons = ref([]);
function updatePageButtons() {
  let pages = [];
  for (let i = props.page - 3; i < props.page + 3; i++) {
    if (i < 1) continue;
    if (i > props.totalPages) break;
    pages.push(i);
  }
  numberedButtons.value = pages;
}
watch(() => props.totalPages, updatePageButtons);
onMounted(() => {
  updatePageButtons();
});
</script>

<style>
/* Table */
.chc-table {
  width: 100%;
  margin-top: 1rem;
}

.chc-table thead,
.chc-table tbody {
  border-bottom: 1px solid;
}

.chc-table tr {
  height: 44px;
}

.chc-table tbody tr + tr {
  border-top: 1px solid var(--border-color);
}

.chc-table tr th:first-child,
.chc-table tr td:first-child {
  padding-left: 20px;
}

.chc-table tr th:last-child,
.chc-table tr td:last-child {
  padding-right: 20px;
}

.chc-table th {
  font-weight: 700;
}

.chc-table tr td:first-child {
  font-weight: 500;
  color: var(--primary-text-color);
}

.chc-table tr td {
  color: var(--muted-text-color);
  white-space: pre-wrap;
}

/* Controls */
.chc-table-controls {
  display: flex;
  justify-content: space-between;
  gap: 2rem;
}

.chc-table-controls__search-container {
  position: relative;
  flex-grow: 1;
  margin-right: 4rem;
}

.chc-table-controls__search {
  width: 100%;
}

.chc-table-controls__search-icon {
  position: absolute;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
}

.chc-table-controls__buttons {
  display: flex;
  gap: 3rem;
  align-items: center;
}

/* Pagination */
.chc-table-pagination {
  margin-top: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chc-table-pagination__button {
  background: var(--secondary-background-color);
  border: 1px solid var(--border-color);
  border-radius: 5px;
  height: 40px;
  width: 40px;
  padding: 0;
}

.chc-table-pagination__button + .chc-table-pagination__button {
  margin-left: 0.25rem;
}

/* "table__link" usable by parent */
.chc-table .table__link {
  border: 0;
  padding: 0;
  background: 0;
  font-weight: initial;
  color: var(--primary-text-color);
}

.chc-table tbody tr:hover .table__link {
  color: var(--primary-color);
  text-decoration: underline;
  cursor: pointer;
}

.chc-table tbody tr:hover td {
  background: var(--secondary-background-color);
  color: var(--primary-text-color);
}
</style>
