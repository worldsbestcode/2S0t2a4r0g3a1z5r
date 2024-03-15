<style>
.excrypt-input__label, .clamped-number__label, .format-option {
  display: block;
  width: 200px;
}
</style>
<template>
  <div>
    <token-namespace id="tokenNamespace" @changed="namespaceChanged">
    </token-namespace>
    <excrypt-input id="staticLeading" :max-length="32" v-model="staticLeading">
      Leading Characters:
    </excrypt-input>
    <clamped-number id="preserveLeading" min=0 max=99 v-model="preserveLeading">
      Preserve Leading:
    </clamped-number>
    <clamped-number id="preserveTrailing" min=0 max=99 v-model="preserveTrailing">
      Preserve Trailing:
    </clamped-number>
    <div class="format-option">
      <label for="useLuhn" class="format-option__description">Luhn Check:</label>
      <input id="useLuhn" type="checkbox" v-model="useLuhn">
    </div>
    <clamped-number id="maskedLength" min=0 max=99 v-model="maskedLength">
      Padding minimum length:
    </clamped-number>
  </div>
</template>
<script>
import ExcryptInput from 'kmes/components/misc/ExcryptInput';
import TokenNamespace from './TokenNamespace';
import ClampedNumberInput from 'kmes/components/misc/ClampedNumberInput';

export default {
  components: {
    'TokenNamespace': TokenNamespace,
    'clamped-number': ClampedNumberInput,
    'excrypt-input': ExcryptInput,
  },
  data: function () {
    return {
      staticLeading: '',
      preserveLeading: 0,
      preserveTrailing: 0,
      useLuhn: false,
      maskedLength: 0,
      tokenNamespace: 0,
    };
  },
  methods: {
    namespaceChanged: function (val) {
      this.tokenNamespace = val;
      this.valueChanged();
    },
    valueChanged: function () {
      this.$emit('changed', {
        staticLeading: this.staticLeading,
        preserveLeading: this.preserveLeading,
        preserveTrailing: this.preserveTrailing,
        useLuhn: this.useLuhn,
        maskedLength: this.maskedLength,
        tokenNamespace: this.tokenNamespace,
      });
    },
  },
  watch: {
    staticLeading: function () {
      this.valueChanged();
    },
    preserveLeading: function () {
      this.valueChanged();
    },
    preserveTrailing: function () {
      this.valueChanged();
    },
    useLuhn: function () {
      this.valueChanged();
    },
    maskedlength: function () {
      this.valueChanged();
    },
  },
};

</script>
