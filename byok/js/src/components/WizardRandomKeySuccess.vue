<template>
  <div>
    <ul class="wizard-success-ul">
      <li v-if="partKcvs">
        Part checksums:
        <span v-for="partKcv in partKcvs" :key="partKcv" class="checksum">{{
          partKcv
        }}</span>
      </li>
      <li v-if="slot !== undefined && slot !== null">Slot: {{ slot }}</li>
      <li v-if="kcv">
        Checksum: <span class="checksum">{{ kcv }}</span>
      </li>
      <li v-if="tpkSlot">Trusted public key slot: {{ tpkSlot }}</li>
      <li v-if="tpkKcv">
        Trusted public key checksum:
        <span class="checksum">{{ keyChecksum }}</span>
      </li>
    </ul>

    <div v-if="keyBlock" class="wizard-success-div">
      <key-block
        heading="Key Block"
        :key-block="keyBlock"
        file-name="key-block"
      />
    </div>

    <div v-if="privateKeyBlock" class="wizard-success-div">
      <key-block
        heading="Private Key Block"
        :key-block="privateKeyBlock"
        file-name="private-key-block"
      />
    </div>

    <div v-if="clearPublicKeyBlock" class="wizard-success-div">
      <key-block
        heading="Clear Public Key Block"
        :key-block="clearPublicKeyBlock"
        file-name="clear-public-key-block"
      />
    </div>

    <div v-if="publicKeyBlock" class="wizard-success-div">
      <key-block
        heading="Trusted Public Key Block"
        :key-block="publicKeyBlock"
        file-name="public-key-block"
      />
    </div>
  </div>
</template>

<script>
import KeyBlock from "@/components/KeyBlock.vue";

export default {
  components: {
    "key-block": KeyBlock,
  },
  data: function () {
    return {
      partKcvs: null,
      slot: null,
      kcv: null,
      tpkSlot: null,
      tpkKcv: null,
      keyBlock: null,
      clearPublicKeyBlock: null,
      publicKeyBlock: null,
      privateKeyBlock: null,
    };
  },
};
</script>

<style scoped>
span.checksum + span.checksum {
  margin-left: 0.5rem;
}
</style>
