<template>
  <label class="chc-label">
    <span class="chc-label__text">
      {{ title }}
    </span>
    <span v-if="hint" class="chc-label__hint">
      {{ hint }}
    </span>
    <WizardFuzzyInput
      v-model:selected="selected"
      single
      :data="objects"
      :display="
        (host) => {
          return host;
        }
      "
      :keys="['name']"
      no-search-results="No key exchange hosts found"
      placeholder="Search for key exchange host"
    />
  </label>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import WizardFuzzyInput from "@/components/wizard/WizardFuzzyInput.vue";

const emit = defineEmits(["update:selectedObject"]);

const props = defineProps({
  selectedObject: {
    type: Object,
    default: undefined,
  },
  objects: {
    default: [],
  },
  hint: {
    type: String,
    default: undefined,
  },
  title: {
    type: String,
    required: true,
  },
  display: {
    type: Function,
    required: true,
  },
});

const selected = computed({
  get() {
    return props.selectedObject;
  },
  set(value) {
    emit("update:selectedObject", value);
  },
});
</script>

<style scoped>
.selector {
  display: flex;
  cursor: pointer;
  padding: 0rem 0.4rem;
  border: 1px solid var(--border-color);
  border-radius: 3px;
  height: 50px;
  justify-content: space-between;
  align-items: center;
}

.selector__button {
  border-left: 1px solid var(--border-color);
  padding-left: 0.4rem;
}

.selector__empty {
  color: var(--muted-text-color);
}
</style>
