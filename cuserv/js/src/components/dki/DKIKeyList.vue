<template>
  <div class="dki-keys-title">{{ props.title }}</div>
  <div v-for="(key, index) in props.keys" :key="index">
    <div class="dki-key-info">
      <div class="dki-key-info-slot dki-key-info-text">Slot {{ key.slot }}</div>

      <div class="dki-key-info-name dki-key-info-text">
        {{ key.objInfo.name }}
      </div>
      <img
        v-if="!key.required"
        class="dki-button-icon"
        src="/shared/static/close-circle.svg"
        @click="emit('deleteKey', key.objInfo.uuid)"
      />
    </div>
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";

const emit = defineEmits(["deleteKey"]);
const props = defineProps({
  keys: {
    type: Array,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    required: false,
    default: "",
  },
});
</script>

<style scoped>
.dki-keys-title {
  font-weight: 700;
  font-size: 28x;
  text-align: left;
  margin-top: 1.5rem;
  border-bottom: 1.4px solid var(--border-color);
}

.dki-key-info {
  display: flex;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1.4px solid var(--border-color);
}

.dki-key-info-slot {
  text-align: left;
}
.dki-key-info-name {
  margin-left: auto;
  margin-right: auto;
}

.dki-key-info-button {
  margin-left: auto;
}

.dki-key-info-text {
  font-size: 24x;
  color: var(--secondary-text-color);
}

.dki-button-icon {
  width: 25px;
  height: 25px;
  cursor: pointer;
}
</style>
