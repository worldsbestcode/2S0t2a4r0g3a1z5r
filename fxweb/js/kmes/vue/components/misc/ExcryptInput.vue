<style scoped>
.excrypt-input {
  display: flex;
}

.excrypt-input__label {
}

.excrypt-input__input {
}
</style>
<template>
  <div class="excrypt-input">
    <label :for="id" class="excrypt-input__label">
      <slot></slot>
    </label>
    <input
      class="excrypt-input__input"
      v-model="inputValue"
      :id="id"
      :maxlength="maxLength"
    >
  </div>
</template>
<script>
export default {
  props: {
    maxLength: {
      type: Number,
      required: false,
      default: 40,
    },
    value: {
      type: String,
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
    sanitize: function (val) {
      var sanitized = val.replace(/[[\]<>;]/g, '');

      if (sanitized !== this.inputValue) {
        this.inputValue = sanitized;
      }

      this.$emit('input', this.inputValue);
    },
  },
  watch: {
    value: function (val) {
      this.sanitize(val);
    },
    inputValue: function (val) {
      this.sanitize(val);
    },
  },
  mounted: function () {
    this.id = this._uid;
  },
};

</script>
