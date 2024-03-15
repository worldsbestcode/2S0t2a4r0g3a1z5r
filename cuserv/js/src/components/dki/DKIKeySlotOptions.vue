<template>
  <label v-if="component" class="key-slot-options">
    <span class="chc-label__text">
      Key Options
      <span class="chc-label__hint"> metadata of key being injected </span>
    </span>
    <component
      :is="component"
      v-model:options="options"
      :key-type="props.keyType"
    />
  </label>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import { eProtocols } from "$shared/utils/protocol.js";

import IngenicoNarKeyOptions from "@/components/dki/key-options/IngenicoNarKeyOptions.vue";
import KitBridgeKeyOptions from "@/components/dki/key-options/KitBridgeKeyOptions.vue";
import VeriFoneKeyOptions from "@/components/dki/key-options/VeriFoneKeyOptions.vue";

const emit = defineEmits(["update:keySlotRef"]);
const props = defineProps({
  keySlotRef: {
    default: {},
    required: false,
  },
  protocol: {
    type: Number,
    required: true,
  },
  keyType: {
    type: Number,
    required: true,
  },
});

const options = computed({
  get() {
    return props.keySlotRef.options;
  },
  set(value) {
    let keySlotRef = props.keySlotRef;
    keySlotRef.options = value;
    emit("update:keySlotRef", keySlotRef);
  },
});

function keyOptionsComponent() {
  let component = null;
  switch (props.protocol) {
    case eProtocols.eIngenicoKiTBridge:
      component = KitBridgeKeyOptions;
      break;
    case eProtocols.eVeriFonePP1000SE:
    case eProtocols.eVeriFoneIPP8:
      component = VeriFoneKeyOptions;
      break;
    case eProtocols.eIngenicoNar:
      component = IngenicoNarKeyOptions;
      break;
    default:
      break;
  }
  return component;
}

const component = keyOptionsComponent();
</script>

<style scoped>
.key-slot-options {
  margin-top: 1rem;
}

.key-slot-options__container {
  display: flex;
}
.add-button {
  margin-top: 2rem;
}
</style>
