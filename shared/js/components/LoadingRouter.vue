<template>
  <template v-if="state.active">
    <div class="bar bar1" />
    <div class="bar bar2" />
  </template>
</template>

<script setup>
import { reactive } from "vue";

import { useBus } from "$shared/bus.js";

const state = reactive({
  active: false,
});

function activeTrue() {
  state.active = true;
}

function activeFalse() {
  state.active = false;
}

useBus("routerBeforeEach", activeTrue);
useBus("routerAfterEach", activeFalse);
</script>

<style scoped>
.bar {
  position: fixed;
  top: var(--app-header-height);
  width: 50%;
  background: var(--primary-color);
  height: 4px;
  z-index: 1;
  animation-timing-function: linear;
  animation-duration: 2s;
  animation-iteration-count: infinite;
}

.bar1 {
  animation-name: bar1;
}

.bar2 {
  animation-name: bar2;
}

@keyframes bar1 {
  from {
    left: 0%;
  }
  to {
    left: 100%;
  }
}

@keyframes bar2 {
  from {
    left: -100%;
  }
  to {
    left: 0%;
  }
}
</style>
