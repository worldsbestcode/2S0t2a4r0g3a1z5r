<template>
  <div>
    <ul class="wizard-success-ul">
      <li>
        Checksum: <span class="checksum">{{ keyChecksum }}</span>
      </li>
    </ul>
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
      keyChecksum: null,
      publicKeyBlock: null,
    };
  },
};
</script>
