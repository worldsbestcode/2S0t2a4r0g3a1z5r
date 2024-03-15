<template>
  <IdpEditorModal
    title="Delete provider"
    tooltip="Delete provider"
    icon="delete"
    buttonText="DELETE"
    submitDispatch="remove"
    :uuid="props.uuid"
  >
    Are you sure you want to delete {{ store.state.idp.name }}?
  </IdpEditorModal>
</template>

<script setup>
import { defineProps } from "vue";
import { useStore } from "vuex";

import IdpEditorModal from "@/idp/IdpEditorModal.vue";

const store = useStore();

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
});
</script>
