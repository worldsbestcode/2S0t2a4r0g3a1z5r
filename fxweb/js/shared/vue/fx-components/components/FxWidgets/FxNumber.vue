<style>
</style>

<template>
  <div class="form-group">
    <label>
      {{ description }}
    </label>
    <input class="form-control"
      type="number"
      :disabled="disabled"
      :value="value"
      @input="updateValue($event.target.value)"
      :min="min"
      :max="max">
  </div>
</template>

<script>
export default {
  props: [
    'description',
    'disabled',
    'min',
    'max',
    'value',
  ],
  methods: {
    updateValue (value) {
      this.$emit('input', parseInt(value, 10));
    },
  },
};
</script>
