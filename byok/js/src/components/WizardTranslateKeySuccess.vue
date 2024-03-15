<template>
  <div>
    <ul class="wizard-success-ul">
      <li>
        Checksum: <span class="checksum">{{ keyChecksum }}</span>
      </li>
    </ul>
    <div v-if="keyBlock" class="wizard-success-div">
      <key-block
        heading="Key Block"
        :key-block="keyBlock"
        file-name="key-block"
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
      keyBlock: null,
    };
  },
};
</script>
