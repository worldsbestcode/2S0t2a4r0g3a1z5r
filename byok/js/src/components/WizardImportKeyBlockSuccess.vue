<template>
  <div>
    <ul class="wizard-success-ul">
      <li>Slot: {{ slot }}</li>
      <li>
        Checksum: <span class="checksum">{{ keyChecksum }}</span>
      </li>
    </ul>

    <div v-if="clearPublicKeyBlock" class="wizard-success-div">
      <key-block
        heading="Clear Public Key Block"
        :key-block="clearPublicKeyBlock"
        :file-name="`clear-public-key-block-${slot}`"
      />
    </div>

    <div v-if="publicKeyBlock" class="wizard-success-div">
      <key-block
        heading="Trusted Public Key Block"
        :key-block="publicKeyBlock"
        :file-name="`public-key-block-${slot}`"
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
      slot: null,
      keyChecksum: null,
      clearPublicKeyBlock: null,
      publicKeyBlock: null,
    };
  },
};
</script>
