<template>
  <div class="icon-button">
    <div class="tooltip-container" :data-tooltip="tooltip">
      <span class="material-symbols-outlined tooltip-button-icon">
        {{ icon }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

defineProps({
  tooltip: {
    type: String,
    default: "",
  },
  icon: {
    type: String,
    required: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});
</script>

<style>
/* Tooltips */
.tooltip-container {
  position: relative;
}

.tooltip-container::after {
  content: attr(data-tooltip);
  display: none;
  position: absolute;
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 1;
  top: -30px;
  /* Adjust this value to position the tooltip */
  left: 50%;
  transform: translateX(-50%);
}

.tooltip-container:hover::after {
  display: block;
}

.tooltip-button-icon {
  width: fit-content;
}

.tooltip-button-icon:hover {
  text-decoration: underline;
  cursor: pointer;
}
.icon-button {
  flex: 0.3;
}
</style>
