<template>
  <div class="deployed-service-main__wrapper">
    <main class="deployed-service-main">
      <div class="deployed-service-main__name" :title="props.title">
        {{ props.title }}
        <div class="deployed-service-main__icons">
          <slot name="actions"></slot>
        </div>
      </div>

      <div class="deployed-service-main__description-table">
        <div class="deployed-service-main__description">
          {{ props.description }}
        </div>
        <table class="deployed-service-main__table">
          <template v-for="[key, value] in props.tableItems" :key="key">
            <tr v-if="value && value.length > 0">
              <th>{{ key }}</th>
              <template v-if="Array.isArray(value)">
                <td>
                  <InformationAndActionsShowButton
                    :show="state.showArray.get(value)"
                    @click="toggleShowArray(value)"
                  />
                  <template v-if="state.showArray.get(value)">
                    <div
                      v-for="(arrayItem, index) in value"
                      :key="index"
                      :title="arrayItem"
                    >
                      {{ arrayItem }}
                    </div>
                  </template>
                </td>
              </template>
              <td v-else :title="value">{{ value }}</td>
            </tr>
          </template>

          <slot name="tableRows"></slot>
        </table>
      </div>

      <div class="deployed-service-main__actions-text">Actions</div>
      <div class="deployed-service-main__actions">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import { defineProps, reactive, watchEffect } from "vue";

import InformationAndActionsShowButton from "@/components/InformationAndActionsShowButton.vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  // key = TH, value = TD
  // left      right
  tableItems: {
    type: Array,
    required: true,
  },
});

const state = reactive({
  showArray: new WeakMap(),
});

function toggleShowArray(key) {
  const current = state.showArray.get(key);
  state.showArray.set(key, !current);
}

watchEffect(() => {
  for (const [, value] of props.tableItems) {
    if (Array.isArray(value)) {
      state.showArray.set(value, false);
    }
  }
});
</script>

<style>
.deployed-service-main__description-table {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(24rem, 1fr));
  gap: 4rem;
}

.deployed-service-main__description {
  color: var(--secondary-text-color);
  font-size: 14px;
  white-space: pre-line;
}

.deployed-service-main__table tr {
  height: 40px;
}

.deployed-service-main__table tr + tr {
  border-top: 1px solid var(--border-color);
}

.deployed-service-main__table th {
  text-align: left;
  font-weight: 500;
  padding: 0.5rem 0;
  padding-right: 0.5rem;
  vertical-align: baseline;
  white-space: nowrap;
}

.deployed-service-main__table td {
  padding: 0.5rem 0;
  text-align: right;
  color: var(--muted-text-color);
  overflow-wrap: anywhere;
}
</style>
