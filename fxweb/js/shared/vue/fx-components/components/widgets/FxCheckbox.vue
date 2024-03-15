<style>
</style>

<template>
  <div class="checkbox">
    <label>
      <input
        type="checkbox"
        :disabled="disabled"
        :checked="value"
        @change="onChange">
      {{ description }}
    </label>
  </div>
</template>

<script>
export default {
  props: [
    'description',
    'disabled',
    'value',
  ],
  methods: {
    onChange () {
      this.$emit('input', !this.value);
    },
  },
};
</script>
