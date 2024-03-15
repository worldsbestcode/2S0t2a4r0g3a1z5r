<template>
  <Modal :title="props.title">
    <template #button="{ on }">
      <ChcButton img="/shared/static/element-plus.svg" v-on="on">
        ADD NEW
      </ChcButton>
    </template>
    <template #content="{ toggleModal }">
      <component
        :is="props.body"
        v-bind="$attrs"
        @cancel="toggleModal"
        @finished="toggleModal"
      />
    </template>
  </Modal>
</template>

<script setup>
import { defineProps } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import Modal from "$shared/components/Modal.vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  body: {
    type: Object,
    required: true,
  },
});
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>
