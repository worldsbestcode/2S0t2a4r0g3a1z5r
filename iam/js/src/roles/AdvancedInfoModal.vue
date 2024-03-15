<template>
  <EditorModal
    title="Advanced Information"
    tooltip="Advanced configuration"
    icon="settings"
    :uuid="props.uuid"
  >
    <AdvancedInfo> </AdvancedInfo>
  </EditorModal>
</template>

<script setup>
import { defineProps } from "vue";

import EditorModal from "@/components/EditorModal.vue";
import AdvancedInfo from "@/roles/AdvancedInfo.vue";

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
});
</script>
