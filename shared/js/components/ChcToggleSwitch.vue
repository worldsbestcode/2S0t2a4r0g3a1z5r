<template>
  <!-- 
    https://github.com/vuejs/vue/issues/5886#issuecomment-308625735
    todo: $.uid is illegal, consider UUID library or something 
  -->
  <div
    class="chc-toggle-switch"
    :class="props.small && 'chc-toggle-switch--small'"
  >
    <input
      :id="$.uid.toString()"
      class="chc-toggle-switch__checkbox"
      type="checkbox"
      :checked="props.modelValue"
      @change="handleChange"
    />
    <label :for="$.uid.toString()" class="chc-toggle-switch__label" />
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: {
    type: Boolean,
  },
  small: {
    type: Boolean,
  },
});

function handleChange(event) {
  // https://github.com/vuejs/vue/issues/7506#issuecomment-359487991
  emit("update:modelValue", event.target.checked);
  event.target.checked = props.modelValue;
}
</script>

<style scoped>
/* inspired by https://codepen.io/alvarotrigo/pen/abVPyaJ */
.chc-toggle-switch {
  --checkbox-width: 80px;
  --checkbox-height: 40px;
  --circle-margin: 3px;
  --circle-size: calc(var(--checkbox-height) - (var(--circle-margin) * 2));

  width: var(--checkbox-width);
}

.chc-toggle-switch--small {
  --checkbox-width: 70px;
  --checkbox-height: 35px;
}

.chc-toggle-switch__checkbox {
  display: none;
}

.chc-toggle-switch__checkbox:checked + .chc-toggle-switch__label {
  background: var(--primary-color);
}

.chc-toggle-switch__checkbox:checked + .chc-toggle-switch__label:after {
  left: calc(100% - var(--circle-margin));
  transform: translateX(-100%);
}

.chc-toggle-switch__label {
  background: var(--border-color);
  display: block;
  cursor: pointer;

  width: var(--checkbox-width);
  height: var(--checkbox-height);
  border-radius: calc(var(--checkbox-height) / 2);
  position: relative;
}

.chc-toggle-switch__label:after {
  background: var(--primary-background-color);
  content: "";
  position: absolute;
  top: var(--circle-margin);
  left: var(--circle-margin);
  width: var(--circle-size);
  height: var(--circle-size);
  border-radius: calc(var(--circle-size) / 2);
  transition: 0.25s;
}

.chc-toggle-switch__label:active:after {
  width: calc(var(--circle-size) * 1.25);
}
</style>
