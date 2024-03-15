<template>
  <div class="service-template-item-deploy-wrapper">
    <component
      :is="props.is"
      class="service-template-item-deploy"
      v-bind="$attrs"
      @click.stop
    >
      <slot />
      <span v-if="!props.noArrow" class="material-symbols-outlined">
        trending_flat
      </span>
    </component>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  is: {
    type: [Object, String],
    required: true,
  },

  noArrow: {
    type: Boolean,
  },
});
</script>

<script>
export default {
  inheritAttrs: false, // Stop wrapper div from receiving click event
};
</script>
