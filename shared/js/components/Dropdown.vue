<!-- eslint-disable-line vue/multi-word-component-names  -->
<template>
  <div class="shared-dropdown">
    <slot name="button" :on="{ click: toggleDropdown }" />
    <div
      v-show="state.showDropdown"
      :class="[$attrs.class, props.right && 'shared-dropdown__dropdown--right']"
      class="shared-dropdown__dropdown"
      @click.stop
    >
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  inheritAttrs: false,
};
</script>

<script setup>
import { defineProps, reactive } from "vue";

const props = defineProps({
  right: {
    type: Boolean,
    default: false,
  },
});

const state = reactive({
  showDropdown: false,
});

function toggleDropdown() {
  state.showDropdown = !state.showDropdown;

  if (state.showDropdown) {
    setTimeout(() => {
      document.addEventListener(
        "click",
        () => {
          if (state.showDropdown) {
            state.showDropdown = false;
          }
        },
        { once: true }
      );
    });
  }
}
</script>

<style>
.shared-dropdown {
  position: relative;
}

.shared-dropdown__dropdown {
  width: max-content;
  position: absolute;
  z-index: 1;

  box-shadow: 0px 0px 26.25px 0px #00000040;
  background: var(--primary-background-color);
  padding: 16px 24px;
  padding-top: 0;
  border-radius: 10px;
}

.shared-dropdown__dropdown header {
  font-size: 20px;

  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-color);
  /* Prefer to let header space the top instead of the dropdown using padding-top */
  margin-top: 16px;
  margin-bottom: 12px;
}

.shared-dropdown__dropdown--right {
  right: 0;
}
</style>
