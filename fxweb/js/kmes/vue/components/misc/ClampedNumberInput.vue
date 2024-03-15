<style scoped>
.clamped-number {
  display: flex;
}

.clamped-number__label {
}

.clamped-number__input {
}
</style>
<template>
  <div class="clamped-number">
    <label :for="id" class="clamped-number__label">
      <slot></slot>
    </label>
    <input
      class="clamped-number__input"
      type="number"
      :id="id"
      v-model="inputValue"
      :max="max"
      :min="min"
    >
  </div>
</template>
<script>
import _ from 'lodash';

export default {
  props: {
    min: {
      required: false,
      default: 0
    },
    max: {
      required: false,
      default: 65535,
    },
    value: {
      required: false,
      default: '',
    },
  },
  data: function () {
    return {
      inputValue: this.value,
      id: null,
    };
  },
  methods: {
    clampValue: function (val) {
      var clamped = _.clamp(val, this.min, this.max);

      if (clamped !== this.inputValue) {
        this.inputValue = clamped;
      }

      this.$emit('input', this.inputValue);
    }
  },
  watch: {
    value: function (val) {
      this.clampValue(val);
    },
    inputValue: function (val) {
      this.clampValue(val);
    }
  },
  mounted: function () {
    this.id = this._uid;
  },
};

</script>
