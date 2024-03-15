<template>
  <EditorModal
    title="Delete role"
    tooltip="Delete role"
    icon="delete"
    buttonText="DELETE"
    submitDispatch="remove"
    :uuid="props.uuid"
    storeType="role"
  >
    Are you sure you want to delete {{ store.state.role.name }}?
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
