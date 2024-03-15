<template>
  <main class="stubs-table">
    <div class="stubs-table__title">{{ props.title }}</div>
    <div class="stubs-table__description">
      {{ props.description }}
    </div>

    <nav class="stubs-table-controls">
      <div class="stubs-table-controls__search-container">
        <input
          v-model="state.search"
          class="stubs-table-controls__search chc-input"
          placeholder="Search keyword"
        />
        <img
          class="stubs-table-controls__search-icon"
          src="/shared/static/search-icon.svg"
        />
      </div>

      <div class="stubs-table-controls__buttons">
        <slot name="batchExportButton" />

        <slot name="exportButton">
          <button class="button-no-styling" @click="exportToCsv">
            <img src="/shared/static/export-to-csv.svg" />Export to CSV
          </button>
        </slot>

        <slot name="addButton" />
      </div>
    </nav>

    <table ref="tableRef" class="deployed-manage-table">
      <thead>
        <tr>
          <th v-for="header in props.headers" :key="header">{{ header }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="props.loading">
          <td :colspan="props.headers.length" style="text-align: center">
            <LoadingSpinner
              :loading="props.loading"
              style="display: inline-block"
            />
          </td>
        </tr>
        <tr v-else-if="filteredData.length === 0">
          <td :colspan="props.headers.length" style="text-align: center">
            {{ props.emptyMessage }}
          </td>
        </tr>
        <template v-else>
          <slot :data="filteredData" name="tableRows" />
        </template>
      </tbody>
    </table>

    <ChcPagination
      v-if="!props.hidePagination"
      v-model:page="page"
      v-model:pageSize="pageSize"
      v-model:totalPages="totalPages"
    />
  </main>
</template>

<script setup>
import Fuse from "fuse.js";
import {
  computed,
  defineEmits,
  defineProps,
  reactive,
  ref,
  watchEffect,
} from "vue";
import { useToast } from "vue-toastification";

import ChcPagination from "$shared/components/ChcPagination.vue";
import LoadingSpinner from "$shared/components/LoadingSpinner.vue";
import { arrayToCsv, download } from "$shared/utils/misc";

let fuse;
const toast = useToast();

const emit = defineEmits([
  "update:page",
  "update:totalPages",
  "update:pageSize",
]);

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  emptyMessage: {
    type: String,
    required: true,
  },

  headers: {
    type: Array,
    required: true,
  },
  searchKeys: {
    type: Array,
    required: true,
  },
  data: {
    type: Array,
    required: true,
  },

  loading: {
    type: Boolean,
    required: true,
  },

  hidePagination: {
    type: Boolean,
  },
  page: {
    type: Number,
    default: undefined,
  },
  pageSize: {
    type: Number,
    default: undefined,
  },
  totalPages: {
    type: Number,
    default: undefined,
  },

  exportName: {
    type: String,
    required: true,
  },
});

const tableRef = ref(null);

const state = reactive({
  search: "",
});

const page = computed({
  get: () => props.page,
  set: (value) => emit("update:page", value),
});
const totalPages = computed({
  get: () => props.totalPages,
  set: (value) => emit("update:totalPages", value),
});
const pageSize = computed({
  get: () => props.pageSize,
  set: (value) => emit("update:pageSize", value),
});

const filteredData = computed(() =>
  state.search ? fuse.search(state.search).map((x) => x.item) : props.data,
);

function exportToCsv() {
  if (filteredData.value.length === 0) {
    toast("No data to export");
    return;
  }

  const table = tableRef.value;

  const headerRow = table.querySelector("thead > tr");
  const tableHeadersArray = [];
  for (const th of headerRow.children) {
    tableHeadersArray.push(th.textContent);
  }

  const bodyRows = table.querySelectorAll("tbody > tr");
  const tableRowsArray = [];
  for (const bodyRow of bodyRows) {
    const tableRowArray = [];
    for (const td of bodyRow.children) {
      tableRowArray.push(td.textContent);
    }
    tableRowsArray.push(tableRowArray);
  }

  const actionsIndex = tableHeadersArray.findIndex((x) => x === "Actions");
  if (actionsIndex !== -1) {
    tableHeadersArray.splice(actionsIndex, 1);
    for (const item of tableRowsArray) {
      item.splice(actionsIndex, 1);
    }
  }

  const csv = arrayToCsv([tableHeadersArray, ...tableRowsArray]);

  const fileName = `${props.exportName}-p${props.page}.csv`.replaceAll(
    " ",
    "_",
  );

  download(csv, fileName);
}

watchEffect(() => {
  const fuseOptions = {
    keys: props.searchKeys,
    includeMatches: true,
    ignoreLocation: true,
    threshold: 0.3,
  };
  fuse = new Fuse([], fuseOptions);
});

watchEffect(() => {
  fuse.setCollection(props.data);
});
</script>

<style scoped>
.stubs-table {
  padding: 0 2rem;
  max-width: 80rem;
  margin: auto;
}

.stubs-table__title {
  font-weight: 700;
  font-size: 28px;
}

.stubs-table__description {
  color: var(--secondary-text-color);
  margin-bottom: 3.5rem;
  white-space: pre-line;
}

.stubs-table-controls {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 2rem;
}

.stubs-table-controls__search-container {
  position: relative;
  flex-grow: 1;
  margin-right: 4rem;
}

.stubs-table-controls__search {
  width: 100%;
}

.stubs-table-controls__search.chc-input {
  min-width: initial;
}

.stubs-table-controls__search-icon {
  position: absolute;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
}

.stubs-table-controls__buttons {
  display: flex;
  gap: 3rem;
  align-items: center;
}
</style>
