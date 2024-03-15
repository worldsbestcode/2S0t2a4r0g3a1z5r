<style lang="scss" scoped>
[hidden] {
  display: none !important;
}
</style>
<template>
  <label class="btn btn-default">
    <slot></slot>
    <input
      type="file"
      :accept="accept"
      @change="fileChanged"
      hidden
    >
  </label>
</template>
<script>
export default {
  props: {
    // which File types are allowed
    accept: {
      type: String,
      default: '',
    },
  },
  methods: {
    /**
     * Reads the file data, and sets fileData (which updates the displayed file data)
     *
     * @param e The input event after selecting a file.
     */
    fileChanged: function (e) {
      this.$emit('change', e);
    },
  }
};
</script>
