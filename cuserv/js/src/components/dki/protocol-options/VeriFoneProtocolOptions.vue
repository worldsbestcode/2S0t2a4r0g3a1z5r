<template>
  <ChcToggle
    v-model:modelValue="useTdes"
    small
    side="right"
    label="Use TDES"
  ></ChcToggle>
  <ChcToggle
    v-model:modelValue="clearKeys"
    small
    side="right"
    label="Clear Keys"
    hint="clear master session and KTK keys, may add 6 seconds to injection time"
  ></ChcToggle>
  <ChcToggle
    v-if="state.displayEmptyGiskeOption"
    v-model:modelValue="emptyGiske"
    small
    side="right"
    label="Empty GISKE Session Support"
  ></ChcToggle>
  <ChcToggle
    v-if="state.displayZeroKeyOption"
    v-model:modelValue="zeroKeys"
    small
    side="right"
    label="Zero Key Support"
  ></ChcToggle>
</template>

<script setup>
import {
  computed,
  defineEmits,
  defineProps,
  onBeforeMount,
  reactive,
} from "vue";

import ChcToggle from "$shared/components/ChcToggle.vue";
import { eProtocols } from "$shared/utils/protocol";

const emit = defineEmits(["update:options"]);
const props = defineProps({
  options: {
    type: Object,
    requried: true,
  },
  protocol: {
    type: Number,
    required: true,
  },
});

const useTdes = computed({
  get() {
    return props.options.useTdes;
  },
  set(value) {
    let options = props.options;
    options.useTdes = value;
    emit("update:options", options);
  },
});
const clearKeys = computed({
  get() {
    return props.options.clearKeys;
  },
  set(value) {
    let options = props.options;
    options.clearKeys = value;
    emit("update:options", options);
  },
});
const zeroKeys = computed({
  get() {
    return props.options.zeroKey;
  },
  set(value) {
    let options = props.options;
    options.zeroKey = value;
    emit("update:options", options);
  },
});
const emptyGiske = computed({
  get() {
    return props.options.emptyGiske;
  },
  set(value) {
    let options = props.options;
    options.emptyGiske = value;
    emit("update:options", options);
  },
});

const state = reactive({
  displayZeroKeyOption: true,
  displayEmptyGiskeOption: true,
});

onBeforeMount(() => {
  if (props.protocol === eProtocols.eVeriFonePP1000SE) {
    state.displayEmptyGiskeOption = false;
    state.displayZeroKeyOption = false;
  }
});
</script>
