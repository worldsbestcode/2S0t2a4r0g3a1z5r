<style>
</style>

<template>
  <div class="form-group">
    <div :class="{ 'has-error': hasError }">
      <label v-if="description">
        {{description}}
      </label>
      <input class="form-control"
        spellcheck="false"
        type="text"
        :disabled="disabled"
        :value="value"
        @input="updateValue($event.target.value)">
    </div>
  </div>
</template>

<script>
export default {
  props: [
    'description',
    'disabled',
    'value',
  ],
  computed: {
    hasError: function () {
      return this.value.length % 2 === 1;
    },
  },
  methods: {
    convertUpperHex (value) {
      return value.toUpperCase().replace(/[^\dA-F]/g, '');
    },
    updateValue (value) {
      var fixedValue = this.convertUpperHex(value);
      // Must manually fix the value if the user typed an invalid character
      // Reference from a class in the div
      var inputElement = this.$el.querySelector('input');
      inputElement.value = fixedValue;
      this.$emit('input', fixedValue);
    },
  },
};
</script>
