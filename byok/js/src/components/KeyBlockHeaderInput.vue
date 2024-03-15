<template>
  <input :value="modelValue" @input="handleInput" />
</template>

<script>
export default {
  props: {
    modelValue: {
      type: String,
      required: true,
    },
  },
  methods: {
    handleInput: function (event) {
      let upperCaseValue = event.target.value.toUpperCase();
      let isPrintableCharacter = /^[ -~]+$/.test(upperCaseValue);

      let blackList = "[];<>#";
      let containsIllegalCharacter = false;
      for (let character of upperCaseValue) {
        if (blackList.includes(character)) {
          containsIllegalCharacter = true;
        }
      }

      if (
        upperCaseValue === "" ||
        (isPrintableCharacter && !containsIllegalCharacter)
      ) {
        event.target.value = upperCaseValue;
        this.$emit("update:modelValue", upperCaseValue);
      } else {
        event.target.value = this.modelValue;
      }
    },
  },
};
</script>
