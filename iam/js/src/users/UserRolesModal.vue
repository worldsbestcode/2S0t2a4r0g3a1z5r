<template>
  <EditorModal
    :title="
      store.state.user.application ? 'Application Partitions' : 'User Roles'
    "
    :tooltip="props.users ? 'Roles' : 'Partitions'"
    icon="shield"
    :uuid="props.uuid"
    storeType="user"
  >
    <UserRoles :uuid="props.uuid"> </UserRoles>
  </EditorModal>
</template>

<script setup>
import { defineProps } from "vue";
import { useStore } from "vuex";

import EditorModal from "@/components/EditorModal.vue";
import UserRoles from "@/users/UserRoles.vue";

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
  users: {
    type: Boolean,
    default: true,
    required: true,
  },
});

const store = useStore();
</script>
