<template>
  <div class="list-type-container">
    <button
      class="tile-list-button"
      :class="listStyle === 'tile' && 'tile-list-button-active'"
      @click="listStyle = 'tile'"
    >
      <img
        :src="`/shared/static/tile${listStyle === 'tile' ? '-active' : ''}.svg`"
      />
    </button>
    <button
      class="tile-list-button"
      :class="listStyle === 'list' && 'tile-list-button-active'"
      @click="listStyle = 'list'"
    >
      <img
        :src="`/shared/static/list${listStyle === 'list' ? '-active' : ''}.svg`"
      />
    </button>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import { listStyle as listStyleProp } from "$shared/props.js";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: listStyleProp,
});

const listStyle = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit("update:modelValue", value);
  },
});
</script>

<style scoped>
.list-type-container {
  display: flex;
  gap: 0.5rem;
}

.tile-list-button {
  background: 0;
  border: 0;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.tile-list-button-active {
  background: var(--primary-background-color);
  box-shadow: 0px 5px 20px rgba(48, 48, 48, 0.15);
  border-radius: 5px;
}
</style>
