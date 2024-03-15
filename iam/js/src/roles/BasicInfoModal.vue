<template>
  <EditorModal
    title="Basic Information"
    tooltip="Basic information"
    icon="edit"
    :uuid="props.uuid"
    storeType="role"
  >
    <BasicInfo> </BasicInfo>
  </EditorModal>
</template>

<script setup>
import { defineProps } from "vue";

import EditorModal from "@/components/EditorModal.vue";
import BasicInfo from "@/roles/BasicInfo.vue";

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
});
</script>
