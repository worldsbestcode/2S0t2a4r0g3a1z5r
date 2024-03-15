<style>
</style>
<template>
<span>
  <div v-if="innerstyle" :style="innerstyle" :class="columnWidth">
    <slot></slot>
  </div>
  <div v-if="innerstyle" :class="columnWidth">
    <slot></slot>
  </div>
  <div :class="[columnWidth]">
    <slot></slot>
  </div>
</span>
</template>
<script>
export default {
  props: [
    'innerstyle',
    'width'
  ],
  computed: {
    columnWidth: function () {
      return 'col-sm-' + this.width;
    }
  }
};
</script>
