<template>
  <div>
    <div class="panel-heading" role="button">
      <div class="panel-title text-center" @click="toggleValue">
        {{title}}
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    value: {
      required: true,
    },
  },
  methods: {
    toggleValue: function () {
      this.$emit('input', !this.value);
    }
  }
};
</script>
