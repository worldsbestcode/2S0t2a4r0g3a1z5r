<template>
  <EditorModal
    title="Services"
    tooltip="Service permissions"
    icon="lock"
    :uuid="props.uuid"
    storeType="role"
  >
    <ServicePermissions />
  </EditorModal>
</template>

<script setup>
import { defineProps } from "vue";

import EditorModal from "@/components/EditorModal.vue";
import ServicePermissions from "@/roles/ServicePermissions.vue";

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
});
</script>
