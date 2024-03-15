<template>
  <div>
    <div class="field">
      <label class="label">
        Certificate Authority Name
      </label>
      <div class="control">
        <input
          class="input"
          type="text"
          v-model="caData.name"
          placeholder="Required"
          onfocus="this.placeholder=''"
          onblur="this.placeholder='Required'"
        >
      </div>
    </div>
    <div class="field">
      <label class="label">
        PKI Type
      </label>
      <div class="control select select-full-width">
        <select
          type="number"
          v-model.number="caData.pkiType"
        >
          <option v-for="(v, k) in certTypes" :value="k" :key="k">
            {{ v }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
import CertType from 'kmes/store/schema/CertType';
import CertAuthoritySchema from 'kmes/store/schema/CertAuthoritySchema';

export default {
  props: {
    value: {
      type: Object,
      required: true,
    },
    certTypes: {
      type: Array,
      default: function () {
        return CertType.getTypeStrings();
      }
    },
  },
  data: function () {
    var caData = new CertAuthoritySchema();
    caData.fromJSON(this.value);
    return { caData };
  },
  watch: {
    value: {
      handler: function () {
        this.caData.fromJSON(this.value);
      },
      deep: true,
    },
    caData: {
      handler: function () {
        this.$emit('input', this.caData);
      },
      deep: true,
    }
  },
};
</script>
