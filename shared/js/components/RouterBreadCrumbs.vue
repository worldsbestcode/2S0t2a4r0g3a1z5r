<template>
  <div
    class="available-services-bread__wrapper"
    :class="props.mainPadding && 'chc-main-horizontal-padding'"
  >
    <div class="available-services-bread">
      <template v-for="crumb in crumbs.slice(0, -1)" :key="crumb.to">
        <RouterLink :to="crumb.to" :title="crumb.name">{{
          crumb.name
        }}</RouterLink
        >/</template
      >
      <RouterLink
        class="available-services-bread__current"
        :to="crumbs.slice(-1)[0].to"
      >
        {{ crumbs.slice(-1)[0].name }}
      </RouterLink>
    </div>
  </div>

  <div v-if="props.seperator" class="available-services-seperator" />
</template>

<script setup>
import { computed, defineProps } from "vue";

import { useCrumbs } from "$shared/composables.js";

// todo: Update all usages of RouterBreadCrumbs

const props = defineProps({
  crumbs: {
    type: Array,
    default: () => [],
  },
  seperator: {
    type: Boolean,
  },
  mainPadding: {
    type: Boolean,
  },
});

const crumbs = computed(() => {
  if (props.crumbs.length === 0) {
    return useCrumbs().value;
  } else {
    return props.crumbs;
  }
});
</script>

<style scoped>
.available-services-bread__wrapper {
  margin: 2rem 0;
  padding: 0 2rem;
}

.available-services-bread {
  display: flex;
  gap: 0.5rem;
  color: var(--border-color);
  align-items: center;
  flex-wrap: wrap;
  max-width: 80rem;
  margin: auto;
}

.available-services-bread a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.available-services-bread a:hover {
  text-decoration: underline;
}

a.available-services-bread__current {
  pointer-events: none;
  color: var(--secondary-text-color);
}

.available-services-seperator {
  min-height: 1px;
  background: var(--border-color);
}
</style>
