<template>
  <EditorModal
    title="Unarchive role"
    tooltip="Unarchive role"
    icon="lock_open"
    buttonText="UNARCHIVE"
    submitDispatch="unarchive"
    :uuid="props.uuid"
    storeType="role"
  >
    Are you sure you want to unarchive {{ store.state.role.name }}?
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
