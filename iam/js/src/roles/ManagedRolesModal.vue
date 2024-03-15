<template>
  <EditorModal
    title="Managed Roles"
    tooltip="Managed roles"
    icon="assignment_ind"
    :uuid="props.uuid"
    storeType="role"
  >
    <ManagedRoles :uuid="props.uuid"> </ManagedRoles>
  </EditorModal>
</template>

<script setup>
import { defineProps } from "vue";

import EditorModal from "@/components/EditorModal.vue";
import ManagedRoles from "@/roles/ManagedRoles.vue";

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
});
</script>
