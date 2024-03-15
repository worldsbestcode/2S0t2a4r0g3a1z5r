<style>
.excrypt-input__label {
  display: block;
  width: 200px;
}
</style>
<template>
  <div>
    <excrypt-input id="groupName" :max-length="40" @input="updateName" v-model="tokenGroup.name">
      Name:
    </excrypt-input>
    <tokenization-info :keys="keys" @changed="updateTokenizationInfo">
    </tokenization-info>
    <token-format @changed="updateTokenFormat">
    </token-format>
  </div>
</template>
<script>
import ExcryptInput from 'kmes/components/misc/ExcryptInput';
import TokenizationInfo from 'kmes/components/token/TokenizationInfo';
import TokenFormat from 'kmes/components/token/TokenFormat';
import TokenGroupSchema from 'kmes/store/schema/TokenGroupSchema';

export default {
  components: {
    'excrypt-input': ExcryptInput,
    'tokenization-info': TokenizationInfo,
    'token-format': TokenFormat,
  },
  props: {
    tokenGroup: {
      type: Object,
      default () {
        return new TokenGroupSchema();
      }
    },
    keys: {
      type: Array,
      default () {
        return [];
      }
    }
  },
  methods: {
    updateTokenizationInfo: function (tokenizationInfo) {
      this.tokenGroup.keyID = tokenizationInfo.keyID;
      this.tokenGroup.keyName = tokenizationInfo.keyName;
      this.tokenGroup.verifyLength = tokenizationInfo.verifyLength;
      this.tokenGroup.tokenizeDate = tokenizationInfo.tokenizeDate;
      this.tokenGroupChanged();
    },
    updateName: function (name) {
      this.tokenGroup.name = name;
      this.tokenGroupChanged();
    },
    updateTokenFormat: function (tokenFormat) {
      this.tokenGroup.staticLeading = tokenFormat.staticLeading;
      this.tokenGroup.preserveLeading = tokenFormat.preserveLeading;
      this.tokenGroup.preserveTrailing = tokenFormat.preserveTrailing;
      this.tokenGroup.useLuhn = tokenFormat.useLuhn;
      this.tokenGroup.maskedLength = tokenFormat.maskedLength;
      this.tokenGroup.tokenNamespace = tokenFormat.tokenNamespace;
      this.tokenGroupChanged();
    },
    tokenGroupChanged: function () {
      this.$emit('changed', this.tokenGroup);
    },
  }
};
</script>
