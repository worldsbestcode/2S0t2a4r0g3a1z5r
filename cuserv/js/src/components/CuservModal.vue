<template>
  <Modal v-bind="$attrs">
    <template #button="{ on }">
      <ButtonIcon v-if="props.icon" :icon="props.icon" v-on="on" />
      <button
        v-else-if="props.text"
        class="deployed-manage-table__delete"
        v-on.stop="on"
      >
        {{ props.text }}
      </button>
      <button
        v-else-if="action"
        class="deployed-service-main__actions-link"
        v-on.stop="on"
      >
        <img
          class="deployed-service-main__actions-img"
          :src="props.action.imgSrc"
        />
        {{ props.action.text }}
      </button>
    </template>
    <template #content="attributes">
      <slot name="content" v-bind="attributes"></slot>
    </template>
  </Modal>
</template>

<script setup>
import { defineProps } from "vue";

import Modal from "$shared/components/Modal.vue";

import ButtonIcon from "@/components/ButtonIcon.vue";

const props = defineProps({
  icon: {
    type: [String, undefined],
    default: undefined,
  },

  text: {
    type: [String, undefined],
    default: undefined,
  },

  /*
    The prop action ought to be an object such as:
      {
        imgSrc: string,
        text: string
      }
  */
  action: {
    type: [Object, undefined],
    default: undefined,
  },
});
</script>
