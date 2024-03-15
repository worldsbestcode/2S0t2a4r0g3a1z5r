<style scoped>
.token-group-option {
  display: flex;
}

.token-group-option__description, .clamped-number__label {
  display: block;
  width: 200px;
}
</style>
<template>
  <div>
    <div class="token-group-option">
      <label for="keyName" class="token-group-option__description">
        Key:
      </label>
      <select id="keyName" v-model="key">
        <option v-for="key in keys" :value="key" :key="key.objectID">
          {{ key.name }}
        </option>
      </select>
    </div>
    <div class="token-group-option">
      <clamped-number id="verifyLength" min=0 max=99 v-model="verifyLength">
        Verification length:
      </clamped-number>
    </div>
    <div class="token-group-option">
      <label for="tokenizeDate" class="token-group-option__description">
        Tokenize date:
      </label>
      <input id="tokenizeDate" type="checkbox" v-model="tokenizeDate">
    </div>
  </div>
</template>
<script>
import ClampedNumberInput from 'kmes/components/misc/ClampedNumberInput';

export default {
  components: {
    'clamped-number': ClampedNumberInput,
  },
  props: {
    keys: {
      type: Array,
      default () {
        return [];
      }
    }
  },
  data: function () {
    return {
      tokenizeDate: false,
      verifyLength: 0,
      key: {
        objectID: '-1',
        name: '',
      },
    };
  },
  methods: {
    valueChanged: function () {
      this.$emit('changed', {
        keyID: this.key.objectID,
        keyName: this.key.name,
        tokenizeDate: this.tokenizeDate,
        verifyLength: this.verifyLength
      });
    }
  },
  watch: {
    verifyLength: function (val) {
      this.valueChanged();
    },
    key: function (val) {
      this.valueChanged();
    },
    tokenizeDate: function (val) {
      this.valueChanged();
    },
  },
};

</script>
