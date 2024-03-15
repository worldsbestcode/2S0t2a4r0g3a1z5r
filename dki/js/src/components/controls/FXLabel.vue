<template>
  <div class="fx-label" :style="labelStyle">{{ text }}</div>
</template>

<script setup>
import { defineProps, ref, onBeforeMount } from "vue";
const props = defineProps({
  text: {
    type: String,
    required: false,
    default: "",
  },
  theme: {
    type: String,
    required: false,
    default: "primary", // secondary, muted are the other options.
  },
  color: {
    type: String,
    required: false,
    default: "",
  },
});

const labelStyle = ref({});

onBeforeMount(() => {
  let color = props.color;

  if (!color) {
    switch (props.theme) {
      case "secondary":
        color = "var(--secondary-text-color)";
        break;
      case "muted":
        color = "var(--muted-text-color)";
        break;
      case "primary":
      default:
        color = "var(--primary-text-color)";
        break;
    }
  }

  labelStyle.value = {
    color: color,
  };
});
</script>

<style scoped>
.fx-label {
  height: fit-content;
  white-space: pre-line;
}
</style>
