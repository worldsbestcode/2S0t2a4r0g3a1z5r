<template>
  <EditorModal
    title="Delete identity"
    tooltip="Delete identity"
    icon="delete"
    buttonText="DELETE"
    submitDispatch="remove"
    :uuid="props.uuid"
    storeType="user"
  >
    Are you sure you want to delete {{ store.state.user.username }}?
  </EditorModal>
</template>

<script setup>
import { defineProps } from "vue";
import { useStore } from "vuex";

import EditorModal from "@/components/EditorModal.vue";

const store = useStore();

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
});
</script>
