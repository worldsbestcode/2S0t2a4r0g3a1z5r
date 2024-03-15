<template>
  <form class="form-inline">
    <div class="form-group">
      <label>Major key:</label>
      <select class="form-control" v-model="selected">
        <option v-for="key in majorKeys" :key="key">
          {{ key }}
        </option>
      </select>
    </div>
  </form>
</template>
<script>
export default {
  props: {
    majorKeys: {
      type: Array,
      required: true,
    },
    majorKey: {
      type: String,
      required: true,
    },
  },
  data () {
    return {
      selected: this.majorKey,
    };
  },
  watch: {
    selected () {
      this.$emit('update:majorKey', this.selected);
    },
    majorKey () {
      this.selected = this.majorKey;
    },
  },
};
</script>
