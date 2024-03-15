<template>
  <ChcModal ref="chcModalRef" v-bind="$attrs">
    <template #button="{ on }">
      <slot name="button" :on="on" />
    </template>

    <slot />

    <ModalFooter
      :text="props.actionText"
      :loading="props.loading"
      @action="action"
      @cancel="cancel"
    />
  </ChcModal>
</template>

<script setup>
import { defineEmits, defineProps, ref } from "vue";

import ChcModal from "$shared/components/ChcModal.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

const emit = defineEmits(["action", "cancel"]);

const props = defineProps({
  actionText: {
    type: String,
    default: "Confirm",
  },
  loading: {
    type: Boolean,
  },
  actionCloses: {
    type: Boolean,
  },
});

const chcModalRef = ref();

function action() {
  emit("action");

  if (props.actionCloses) {
    chcModalRef.value.toggleModal();
  }
}

function cancel() {
  emit("cancel");

  chcModalRef.value.toggleModal();
}
</script>
