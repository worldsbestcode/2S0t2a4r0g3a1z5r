<style>
</style>
<template>
<div>
  <label v-if="label">{{label}}</label>
  <div class="input-group" v-if="iconclass">
    <!-- <span class="input-group-addon">
      <i class="fa fa-{{iconclass}}"></i>
    </span>-->
    <input v-if="!regex"
      class="form-control"
      type="text"
      data-inputmask-mask="mask"
      :value="value"
      @input="updateValue($event.target.value)">

    <div v-if="regex" :class="{'has-error': invalid}">
      <input class="form-control"
        type="text"
        :value="value"
        @input="updateValue($event.target.value)"
        :disabled="disabled"
        @blur="onBlurEvent">
    </div>
  </div>

  <div v-if="!iconclass">
    <input v-if="!regex"
      class="form-control"
      type="text"
      data-inputmask-mask="mask"
      :value="value"
      @input="updateValue($event.target.value)"
      :disabled="$disabled"
      @blur="blurCallback">

    <div v-if="regex" :class="{'has-error': invalid}">
      <input
        class="form-control"
        type="text"
        :value="value"
        @input="updateValue($event.target.value)"
        :disabled="disabled"
        :maxlength="maxLength"
        @blur="onBlurEvent">
    </div>
  </div>
</div>
</template>
<script>
import FxStringUtils from 'shared/FxStringUtils';

export default {
  data: function () {
    return {
      lastValidStr: '',
      invalid: false,
      formInvalid: true
    };
  },
  props: [
    'label',
    'iconclass',
    'mask',
    'disabled',
    'regex',
    'csvregex',
    'forceregex',
    'restrict',
    'required',
    'whenblurred',
    'value',
    'maxLength'
  ],
  methods: {
    updateInvalid: function (inputValue, validatedInputValue) {
      this.invalid = (inputValue.length() === 0) || (validatedInputValue === '' && inputValue !== '');
      this.formInvalid = inputValue === '' && this.required ? true : this.invalid;

      this.$emit('update:form-invalid', this.formInvalid);
    },
    checkRegexInput: function (inputValue) {
      let sanitizedValue = this.sanitizeInput(inputValue, this.restrict_regexp);
      let result = this.getValidInput(sanitizedValue, this.mask_regexp);

      // Update invalid
      this.updateInvalid(inputValue, result);

      // Allow the user to clear out the field
      // If the input was invalid, do not cache the result
      this.lastValidStr = sanitizedValue && result ? result : '';
    },
    sanitizeInput: function (str, regex) {
      if (str) {
        return str.replace(regex, '');
      } else {
        return '';
      }
    },
    regexForCSV: function (str, regex) {
      return 'false';
    },
    getValidInput: function (str, regex) {
      // Determine whether to interpret the string as CSV and validate
      // each item, or just validate the the raw string
      if (this.csvregex === true) {
        return FxStringUtils.regexForCSV(str, regex) ? str : '';
      } else {
        let results = str.match(regex);

        if (results) {
          return results[0] === str ? str : '';
        }

        return '';
      }
    },
    revertInput: function () {
      // Revert to last valid input
      this.checkRegexInput();

      // Leave input alone if not enforcing the regex mask
      if (this.forceregex !== false) {
        this.value = this.lastValidStr;
        this.updateInvalid(false);
      }
    },
    updateValue: function (inputValue) {
      if (this.regex) {
        this.checkRegexInput(inputValue);
      }
      this.$emit('input', inputValue);
    },
    blurCallback: function () {
      if (this.whenblurred) {
        this.whenblurred();
      }
    },
    onBlurEvent: function () {
      if (this.forceRegex) {
        this.value = this.lastValidStr;
        this.updateInvalid(this.value, this.value);
      }
    }
  },
  computed: {
    mask_regexp: function () {
      if (this.regex) {
        return new RegExp(this.mask ? this.mask : '', 'g');
      }
    },
    restrict_regexp: function () {
      if (this.regex) {
        return new RegExp(this.restrict ? this.restrict : '', 'g');
      }
    }
  },
};
</script>
