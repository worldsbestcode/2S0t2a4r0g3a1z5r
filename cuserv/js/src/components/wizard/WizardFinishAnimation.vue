<template>
  <div class="finish-wrapper">
    <img class="finish-icon" :src="templateData?.params?.details?.icon" />

    <div class="finish-container">
      <div class="finish-image-container">
        <img
          class="finish-checkmark"
          src="/shared/static/deployed-checkmark.svg"
        />
      </div>
      <div class="finish-image-container">
        <img class="finish-circle" src="/shared/static/deployed-circle.svg" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject } from "vue";

const templateData = inject("templateData");
</script>

<style scoped>
.finish-wrapper {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 2rem auto;
}

.finish-icon {
  position: absolute;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.finish-container {
  position: relative;
  background: white;
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.finish-image-container {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

.finish-checkmark {
  /* align checkmark with circle */
  transform: translate(28px, -10px);
}

.finish-circle {
  clip-path: circle(50% at -50% 50%);
  animation-name: circle-mask;
  animation-duration: 0.5s;
  animation-fill-mode: forwards;
  animation-timing-function: ease-in-out;
}

.finish-checkmark {
  clip-path: circle(100px at -100px 50%);
  animation-name: checkmark-mask;
  animation-duration: 0.5s;
  animation-fill-mode: forwards;
  animation-timing-function: ease-in-out;

  animation-delay: 0.5s;
}

.finish-container {
  animation-name: container;
  animation-duration: 0.5s;
  animation-fill-mode: forwards;
  animation-timing-function: ease-in-out;

  animation-delay: 1s;
}

.finish-icon {
  transform: scale(0);
  animation-name: icon;
  animation-duration: 0.5s;
  animation-fill-mode: forwards;
  animation-timing-function: ease-in-out;

  animation-delay: 1s;
}

@keyframes circle-mask {
  to {
    clip-path: circle(50% at 50% 50%);
  }
}

@keyframes checkmark-mask {
  to {
    clip-path: circle(100px at 50% 50%);
  }
}

@keyframes container {
  to {
    transform: scale(0.4) translate(100%, 50%);
  }
}

@keyframes icon {
  to {
    transform: initial;
  }
}
</style>
