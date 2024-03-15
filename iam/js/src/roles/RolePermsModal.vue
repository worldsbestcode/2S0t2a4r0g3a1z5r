<template>
  <EditorModal
    title="Management Permissions"
    tooltip="Management Permissions"
    icon="list_alt"
    :uuid="props.uuid"
    storeType="role"
  >
    <RolePerms> </RolePerms>
  </EditorModal>
</template>

<script setup>
import { defineProps } from "vue";

import EditorModal from "@/components/EditorModal.vue";
import RolePerms from "@/roles/RolePerms.vue";

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
});
</script>
