<template>
  <EditorModal
    :title="
      store.state.user.application ? 'Authentication' : 'User Authentication'
    "
    tooltip="Authentication"
    icon="badge"
    :uuid="props.uuid"
    storeType="user"
  >
    <UserAuth :uuid="props.uuid"> </UserAuth>
  </EditorModal>
</template>

<script setup>
import { defineProps } from "vue";
import { useStore } from "vuex";

import EditorModal from "@/components/EditorModal.vue";
import UserAuth from "@/users/UserAuth.vue";

const store = useStore();

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
});
</script>
