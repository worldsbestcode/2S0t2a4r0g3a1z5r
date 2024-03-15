<template>
  <component :is="props.is" class="service-template-item" v-bind="$attrs">
    <div v-if="props.imgSrc" class="service-template-item-icon">
      <img :src="props.imgSrc" />
    </div>
    <div class="service-template-item-name-vendor-container">
      <div class="service-template-item-name">
        {{ props.name }}
      </div>
      <div class="service-template-item-vendor">
        {{ props.description }}
      </div>
    </div>

    <slot />
  </component>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  is: {
    type: [Object, String],
    required: true,
  },

  imgSrc: {
    type: [String, undefined],
    default: undefined,
  },
  name: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
});
</script>
