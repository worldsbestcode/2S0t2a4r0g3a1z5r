<template>
  <button class="icon-with-hover">
    <img :src="`/shared/static/${$props.icon}.svg`" />
    <img :src="`/shared/static/${$props.icon}-active.svg`" />
  </button>
</template>

<script setup>
import { defineProps } from "vue";

defineProps({
  icon: {
    type: String,
    required: true,
  },
});
</script>
