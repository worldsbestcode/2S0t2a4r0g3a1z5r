<template>
  <div class="search">
    <div class="search-icon">
      <img :src="'/shared/static/search-icon.svg'" />
    </div>

    <input
      ref="searchInputRef"
      v-model="search"
      type="search"
      class="search-input"
      placeholder="Search for a service"
    />

    <button v-if="search" class="search-delete" @click="search = ''">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineExpose, defineProps, ref } from "vue";

const searchInputRef = ref();

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: {
    type: String,
    required: true,
  },
});

defineExpose({ input: searchInputRef });

const search = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit("update:modelValue", value);
  },
});
</script>

<style scoped>
.search {
  border-top-right-radius: inherit;
  border-top-left-radius: inherit;
  position: relative;
  border-bottom: 1px solid var(--border-color);
  width: 100%;
  height: 42px;
}

.search-delete {
  display: flex;
  align-items: center;
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  background: transparent;
  border: 0;
  padding: 0;
  padding-right: 12px;
}

.search-icon {
  position: absolute;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  padding-left: 24px;
  width: 60px;
}

.search-input {
  border-radius: 0;
  border: 0;
  border-top-left-radius: inherit;
  border-top-right-radius: inherit;

  padding: 0;
  padding-left: 60px;

  display: block;
  width: 100%;
  height: 100%;
  outline: 0;

  background: transparent;

  color: var(--primary-text-color);
}

.search-input::placeholder {
  font-weight: 400;
  font-size: 16px;
  color: var(--muted-text-color);
}

.search-icon,
.search-delete {
  color: var(--primary-color);
}
</style>
