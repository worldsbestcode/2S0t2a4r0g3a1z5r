<template>
  <div class="fx-separator" :style="separatorStyle"></div>
</template>

<script setup>
import { defineProps, onBeforeMount, ref } from "vue";

const props = defineProps({
  length: {
    type: String,
    required: false,
    default: "100%",
  },
  thickness: {
    type: String,
    default: "1px",
    required: false,
  },
});

const separatorStyle = ref({});
onBeforeMount(() => {
  separatorStyle.value = {
    borderTopWidth: props.thickness,
    width: props.length,
  };
});
</script>

<style scoped>
.fx-separator {
  border-top: solid var(--border-color);
  margin-left: auto;
  margin-right: auto;
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}
</style>
